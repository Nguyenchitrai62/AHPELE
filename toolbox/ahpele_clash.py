#!/usr/bin/env python3
"""AHPELE geometry check for IFC models: clashes and network connectivity, read back from the FILE.

  python3 ahpele_clash.py model.ifc                       # validation + clashes + connectivity
  python3 ahpele_clash.py model.ifc --tol T --gap G       # penetration tolerance / joint gap, in millimetres
  python3 ahpele_clash.py model.ifc --point X,Y,Z         # distance from each network to a point (mm, world)
  python3 ahpele_clash.py model.ifc --point X,Y           # plan point: distance and elevation range of each network there
  python3 ahpele_clash.py model.ifc --ignore IfcSlab,IfcCovering   # leave classes out of the clash test
  python3 ahpele_clash.py model.ifc --clearance CLASS=MM  # soft clash: keep MM around elements of CLASS
                                                          # (insulation, access or code envelopes the contract states)

--tol is a configurable tolerance: use the clash tolerance the contract states (the default is only a small
numerical allowance for modelling round-off).

Why: a self-check computed from the script's own variables shows what you MEANT to build; any other
software reads the IFC through a geometry engine (world coordinates, placements, units, profiles).
This tool does the same with ifcopenshell, so a wrong unit, a misplaced element or an overlap shows up here.

Validation: ifcopenshell.validate with EXPRESS where-rules (schema-only if the rule engine cannot run);
an invalid entity can make the file unreadable to other tools.

Clashes: ifcopenshell.geom.tree intersection test between every pair of products with a body
(spaces, openings, annotations and spatial elements are skipped); a pair clashes when one solid
penetrates the other by more than --tol. Elements meant to touch (segments meeting at a joint,
equipment standing on a slab) do not count.

Connectivity: routed elements (pipe / duct / cable-carrier / cable segments and fittings) are
grouped by system (IfcRelAssignsToGroup) or else by class + ObjectType; inside each group, elements whose
bounding boxes touch within --gap form one network. Exception: two parallel extruded runs lying side by side
over a length are not joined to each other, however close they are. More than one network in a group means
a break (or separate circuits). Each group also lists its classes/PredefinedTypes.

Close gaps: between different networks, and between a network and everything else, pairs nearer than
--allowance are listed (report only; contact with non-network elements such as supports is left out):
installation tolerance, hangers, insulation and access need that space. 

Through openings: runs inside the box of an element with openings (report only; not every kind of void is recognised).
Needs ifcopenshell (and numpy);
knows nothing about any particular task.
"""
import argparse
import collections
import multiprocessing
import sys

try:
    import ifcopenshell
    import ifcopenshell.geom
    import numpy as np
except ImportError as e:  # pragma: no cover
    sys.exit(f"ahpele_clash needs ifcopenshell and numpy ({e}); pip install ifcopenshell numpy")

SKIP = ("IfcSpace", "IfcOpeningElement", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcAnnotation",
        "IfcGrid", "IfcVirtualElement", "IfcSpatialZone", "IfcProject", "IfcExternalSpatialElement")
# routed runs (segments and the fittings that join them); equipment and terminals stand alone and are not networks
NETWORK = ("IfcFlowSegment", "IfcFlowFitting", "IfcCableCarrierSegment", "IfcCableSegment", "IfcCableFitting",
           "IfcCableCarrierFitting", "IfcPipeSegment", "IfcDuctSegment", "IfcPipeFitting", "IfcDuctFitting")


def label(e):
    n = getattr(e, "Name", None) or ""
    t = getattr(e, "ObjectType", None) or ""
    return f"#{e.id()} {e.is_a()}" + (f" '{n}'" if n else "") + (f" [{t}]" if t and t != n else "")


BOXLIKE = set()  # ids of solids that are axis-aligned boxes (their bounding box is the solid)


def load(path, threads):
    f = ifcopenshell.open(path)
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    tree = ifcopenshell.geom.tree()
    boxes = {}
    it = ifcopenshell.geom.iterator(s, f, threads, exclude=[x for x in f.by_type("IfcProduct")
                                                            if any(x.is_a(k) for k in SKIP)])
    if it.initialize():
        while True:
            shape = it.get()
            tree.add_element(shape)
            v = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3) * 1000.0  # engine output is metres
            if len(v):
                lo, hi = v.min(0), v.max(0)
                boxes[shape.id] = (lo, hi)
                w = v - lo
                corner = ((np.abs(w) <= 0.5) | (np.abs(w - (hi - lo)) <= 0.5)).all()
                if corner and (hi - lo).min() > 0.5:
                    t = w[np.array(shape.geometry.faces, dtype=int).reshape(-1, 3)]
                    vol = abs(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum()) / 6.0
                    if vol >= 0.999 * np.prod(hi - lo):  # a wedge also has all its vertices on box corners
                        BOXLIKE.add(shape.id)
            if not it.next():
                break
    return f, tree, boxes


def sweep(f, eid, scale):
    """(unit direction, length in mm) of an element whose body is one extruded solid, in world axes; else None."""
    try:
        import ifcopenshell.util.placement as up
        e = f.by_id(eid)
        items = [x for r in e.Representation.Representations if r.RepresentationIdentifier in (None, "Body")
                 for x in r.Items]
        if len(items) != 1:
            return None
        it, m = items[0], up.get_local_placement(e.ObjectPlacement)[:3, :3]
        if it.is_a("IfcMappedItem"):
            inner = it.MappingSource.MappedRepresentation.Items
            if len(inner) != 1 or any(getattr(it.MappingTarget, k) for k in ("Axis1", "Axis2", "Axis3") if hasattr(it.MappingTarget, k)):
                return None
            it = inner[0]
        if not it.is_a("IfcExtrudedAreaSolid"):
            return None
        pm = up.get_axis2placement(it.Position)[:3, :3] if it.Position else np.eye(3)
        d = m @ pm @ np.array([float(v) for v in it.ExtrudedDirection.DirectionRatios])
        return d / np.linalg.norm(d), float(it.Depth) * scale
    except Exception:  # unusual representation: no direction, the touch test decides
        return None


def _side_by_side(bi, bj, si, sj):
    """Two parallel swept runs overlapping along their direction by more than their width, centrelines apart."""
    if not si or not sj or abs(si[0] @ sj[0]) < 0.999:
        return False
    d = si[0]
    ci, cj = (bi[0] + bi[1]) / 2, (bj[0] + bj[1]) / 2
    off = cj - ci
    along = float(off @ d)
    lateral = float(np.linalg.norm(off - along * d))
    overlap = (si[1] + sj[1]) / 2 - abs(along)
    # size across the run, from the box corrected for the run's own length (zero-safe for inclined runs)
    wi, wj = (float(np.sort(np.maximum(b[1] - b[0] - np.abs(d) * x[1], 0))[-1]) for b, x in ((bi, si), (bj, sj)))
    wn = [float(np.sort(np.maximum(b[1] - b[0] - np.abs(d) * x[1], 0))[-2]) for b, x in ((bi, si), (bj, sj))]
    return overlap > 1.2 * max(wi, wj, 1.0) and lateral > 0.45 * min(wn + [wi, wj]) and lateral > 1.0


def networks(f, boxes, gap):
    group_of = {}
    for rel in f.by_type("IfcRelAssignsToGroup"):
        g = rel.RelatingGroup
        for o in rel.RelatedObjects or []:
            group_of.setdefault(o.id(), f"{g.is_a()} '{g.Name or g.id()}'")
    groups = collections.defaultdict(list)
    for eid in boxes:
        e = f.by_id(eid)
        if any(e.is_a(k) for k in NETWORK):
            groups[group_of.get(eid) or f"{e.is_a()} [{e.ObjectType or '-'}]"].append(eid)
    try:
        import ifcopenshell.util.unit as uu
        scale = uu.calculate_unit_scale(f) * 1000.0
    except Exception:
        scale = 1.0
    out = {}
    for g, ids in sorted(groups.items()):
        sw = [sweep(f, i, scale) for i in ids]
        lo = np.array([boxes[i][0] for i in ids]) - gap / 2.0  # boxes up to one gap apart touch
        hi = np.array([boxes[i][1] for i in ids]) + gap / 2.0
        parent = list(range(len(ids)))

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(len(ids)):
            touch = np.all((lo[i] <= hi[i + 1:]) & (lo[i + 1:] <= hi[i]), axis=1)
            for j in np.nonzero(touch)[0] + i + 1:
                if not _side_by_side(boxes[ids[i]], boxes[ids[int(j)]], sw[i], sw[int(j)]):
                    parent[root(i)] = root(int(j))
        comps = collections.defaultdict(list)
        for i in range(len(ids)):
            comps[root(i)].append(ids[i])
        out[g] = sorted(comps.values(), key=len, reverse=True)
    return out


def validate(path, limit):
    """Schema + EXPRESS where-rule validation. Returns the number of issues."""
    import logging
    import ifcopenshell.validate

    class Grab(logging.Handler):
        def __init__(self):
            super().__init__()
            self.msgs = []

        def emit(self, record):
            self.msgs.append(record.getMessage())

    f = ifcopenshell.open(path)
    log = logging.getLogger("ahpele_clash.validate")
    log.propagate = False
    grab = Grab()
    log.addHandler(grab)
    log.setLevel(logging.DEBUG)
    mode = "schema + EXPRESS rules"
    try:
        ifcopenshell.validate.validate(f, log, express_rules=True)
    except Exception as e:  # rule executor may need extra modules; fall back to schema-only validation
        grab.msgs.clear()
        mode = f"schema only (EXPRESS rules could not run here: {type(e).__name__}: {e})"
        ifcopenshell.validate.validate(f, log)
    msgs = grab.msgs
    print(f"validation ({mode}): {len(msgs)} issue(s)")
    groups = collections.Counter()
    for m in msgs:
        lines = [x.strip() for x in m.splitlines() if x.strip()]
        rule = next((x for x in lines if x.startswith("Rule ")), lines[0] if lines else m)
        groups[rule[:160]] += 1
    for rule, n in groups.most_common(min(limit, 12)):
        print(f"  {n:5d}  {rule}")
    if msgs:
        print("  first: " + " | ".join(x.strip() for x in msgs[0].splitlines() if x.strip())[:300])
    return len(msgs)


def report_close(tree, elems, net_of, allowance, hard, limit):
    """Smallest gap per pair of groups (network/network, network/class) that are close without being joined."""
    runs = [e for e in elems if e.id() in net_of]
    worst, count, seen = {}, collections.Counter(), set()

    def name(e, n):
        return f"{n[0]} #{n[1] + 1}" if n else e.is_a() + (f" [{e.ObjectType}]" if getattr(e, "ObjectType", None) else "")
    for c in tree.clash_clearance_many(runs, elems, allowance / 1000.0, True) if runs else []:
        x, y, d = c.a, c.b, max(0.0, c.distance * 1000.0)
        k = tuple(sorted((x.id(), y.id())))
        nx, ny = net_of.get(x.id()), net_of.get(y.id())
        if x.id() == y.id() or k in hard or k in seen or (nx and nx == ny):
            continue
        if d <= 1.0 and not (nx and ny):  # standing on, hung from or connected to equipment
            continue
        seen.add(k)
        g = tuple(sorted((name(x, nx), name(y, ny))))
        count[g] += 1
        if g not in worst or d < worst[g][0]:
            worst[g] = (d, x.id(), y.id(), (np.array(list(c.p1)) + np.array(list(c.p2))) / 2 * 1000.0)
    print(f"\nclose gaps (nearer than {allowance:g} mm, report only; set --allowance to the project's value): "
          f"{len(worst)} pair(s) of groups")
    for g, (d, i, j, p) in sorted(worst.items(), key=lambda kv: kv[1][0])[:limit]:
        print(f"  {d:6.1f} mm smallest of {count[g]:3d}  {g[0]}  |  {g[1]}  (#{i}, #{j}) near ({p[0]:.0f}, {p[1]:.0f}, {p[2]:.0f})")
    if len(worst) > limit:
        print(f"  ... {len(worst) - limit} more pair(s) of groups with larger gaps (--limit)")


def has_voids(f, eid):
    """True when the element's body has openings or a profile with voids."""
    e = f.by_id(eid)
    if getattr(e, "HasOpenings", None):
        return True
    try:
        for r in e.Representation.Representations:
            for x in r.Items:
                inner = x.MappingSource.MappedRepresentation.Items if x.is_a("IfcMappedItem") else [x]
                for it in inner:
                    if it.is_a("IfcBooleanResult") or (it.is_a("IfcSweptAreaSolid")
                                                       and it.SweptArea.is_a("IfcArbitraryProfileDefWithVoids")):
                        return True
    except AttributeError:
        pass
    return False


def report_through_voids(f, elems, boxes, net_of, hard, tol, limit):
    """Routed elements inside the box of an element with openings: clear only if the reader subtracts the opening."""
    hosts = [e for e in elems if e.id() not in net_of and has_voids(f, e.id())]
    runs = [e for e in elems if e.id() in net_of]
    out = []
    if hosts and runs:
        lo = np.array([boxes[e.id()][0] for e in runs])
        hi = np.array([boxes[e.id()][1] for e in runs])
        for h in hosts:
            depth = (np.minimum(hi, boxes[h.id()][1]) - np.maximum(lo, boxes[h.id()][0])).min(1)
            out += [(float(depth[k]), h, runs[k]) for k in np.nonzero(depth > tol)[0]
                    if tuple(sorted((h.id(), runs[k].id()))) not in hard]
    if out:
        print(f"\nthrough openings (report only, bounding boxes, so check each): {len(out)} pair(s) where a run lies inside"
              " the box of an element with openings or voids. Confirm each has an opening larger than the run with its"
              " envelope; such a pair is clear only for a check that subtracts the opening")
        for d, h, e in sorted(out, key=lambda r: -r[0])[:limit]:
            print(f"  {d:7.1f} mm  {label(e)}  in  {label(h)}")
        if len(out) > limit:
            print(f"  ... {len(out) - limit} more pair(s) (--limit)")


def box_dist(b, p):
    return float(np.linalg.norm(np.maximum(0, np.maximum(b[0] - p, p - b[1]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ifc")
    ap.add_argument("--tol", type=float, default=1.0, help="penetration that counts as a clash, mm (numerical allowance; "
                    "set it to the project's clash tolerance)")
    ap.add_argument("--gap", type=float, default=1.0, help="joint gap that still connects two elements, mm "
                    "(numerical allowance, like --tol: joints modelled apart by more are reported)")
    ap.add_argument("--allowance", type=float, default=50.0, help="list pairs of different networks, or a network and other "
                    "elements, nearer than this, mm (0 = off; a general coordination figure: set it to the project's value)")
    ap.add_argument("--ignore", default="", help="comma-separated classes left out of the clash test")
    ap.add_argument("--point", action="append", default=[], help="x,y,z (or plan x,y) in mm: report each network's distance (and elevation range near a plan point)")
    ap.add_argument("--clearance", action="append", default=[],
                    help="CLASS=MM: elements of CLASS must stay MM away from every other solid (insulation, envelopes)")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--threads", type=int, default=min(4, multiprocessing.cpu_count()))
    argv = []  # "--point -100,200": argparse would take the value for an option
    for x in sys.argv[1:]:
        if argv and argv[-1] == "--point":
            argv[-1] = "--point=" + x
        else:
            argv.append(x)
    a = ap.parse_args(argv)

    n_invalid = validate(a.ifc, a.limit)
    f, tree, boxes = load(a.ifc, a.threads)
    if not boxes:
        print("no product geometry could be built: check representations, units and placements")
        return 1
    allv = np.array([b for pair in boxes.values() for b in pair])
    lo, hi = allv.min(0), allv.max(0)
    print(f"{len(boxes)} products with a body; model extent (mm, world): "
          f"x {lo[0]:.0f}..{hi[0]:.0f}  y {lo[1]:.0f}..{hi[1]:.0f}  z {lo[2]:.0f}..{hi[2]:.0f}")
    size = hi - lo
    if size.max() > 5e6 or size.max() < 500:
        print(f"WARNING: model is {size.max():.0f} mm across: a unit or placement-scale error is likely")

    centres, widths = collections.defaultdict(list), collections.defaultdict(list)
    for i, b in boxes.items():
        centres[f.by_id(i).is_a()].append((b[0] + b[1]) / 2)
        widths[f.by_id(i).is_a()].append((b[1] - b[0])[:2].max())
    for cls, cs in sorted(centres.items()):
        cs = np.array(cs)
        spread = (cs.max(0) - cs.min(0))[:2].max()
        small = np.median(widths[cls]) < 0.2 * size[:2].max()  # stacked slabs or walls sharing a centre are fine
        if len(cs) >= 3 and small and spread < 0.02 * size[:2].max():
            c = cs.mean(0)
            print(f"WARNING: all {len(cs)} {cls} elements sit within {spread:.0f} mm of ({c[0]:.0f}, {c[1]:.0f}, "
                  f"{c[2]:.0f}) in a model {size[:2].max():.0f} mm across: their placements are probably not "
                  "applied or are in the wrong unit (coordinates in IfcCartesianPoint are in the project length "
                  "unit; a library call may expect SI metres and convert)")

    ignore = tuple(c.strip() for c in a.ignore.split(",") if c.strip())
    elems = [f.by_id(i) for i in boxes if not (ignore and any(f.by_id(i).is_a(c) for c in ignore))]
    clashes = tree.clash_intersection_many(elems, elems, a.tol / 1000.0, True)
    seen, rows = set(), []
    for c in clashes:
        x, y = c.a, c.b
        if x.id() == y.id():
            continue
        k = tuple(sorted((x.id(), y.id())))
        if k in seen:
            continue
        seen.add(k)
        p = (np.array(list(c.p1)) + np.array(list(c.p2))) / 2 * 1000.0
        rows.append((c.distance * 1000.0, x, y, p))
    # axis-aligned boxes (ducts, trays, busway, rectangular insulation envelopes, slabs): exact interval overlap,
    # because a mesh-based test can miss two boxes that share a face plane and overlap along it
    ids = [e.id() for e in elems if e.id() in BOXLIKE]
    if len(ids) > 1:
        lo = np.array([boxes[i][0] for i in ids]); hi = np.array([boxes[i][1] for i in ids])
        for k in range(len(ids) - 1):
            ov = np.minimum(hi[k], hi[k + 1:]) - np.maximum(lo[k], lo[k + 1:])
            depth = ov.min(1)
            for j in np.nonzero(depth > a.tol)[0]:
                i1, i2 = ids[k], ids[k + 1 + j]
                key = tuple(sorted((i1, i2)))
                if key in seen:
                    continue
                seen.add(key)
                cpt = (np.maximum(lo[k], lo[k + 1 + j]) + np.minimum(hi[k], hi[k + 1 + j])) / 2
                rows.append((float(depth[j]), f.by_id(i1), f.by_id(i2), cpt))
    rows.sort(key=lambda r: -r[0])
    nets = networks(f, boxes, a.gap)
    net_of = {i: (g, k) for g, comps in nets.items() for k, c in enumerate(comps) for i in c}  # one connected run
    soft = []
    for spec in a.clearance:
        cls, _, mm = spec.partition("=")
        try:
            gap_mm = float(mm)
        except ValueError:
            print(f"--clearance {spec}: expected CLASS=MM")
            continue
        group = [e for e in elems if e.is_a(cls.strip())]
        if not group:
            print(f"--clearance {spec}: no {cls} elements with a body")
            continue
        hard = {tuple(sorted((r[1].id(), r[2].id()))) for r in rows}
        for c in tree.clash_clearance_many(group, elems, gap_mm / 1000.0, True):
            x, y = c.a, c.b
            k = tuple(sorted((x.id(), y.id())))
            if x.id() == y.id() or k in hard or k in seen:
                continue
            seen.add(k)
            p = (np.array(list(c.p1)) + np.array(list(c.p2))) / 2 * 1000.0
            soft.append((c.distance * 1000.0, gap_mm, x, y, p))
    same = [r for r in rows if net_of.get(r[1].id()) and net_of.get(r[1].id()) == net_of.get(r[2].id())]
    by_cls = collections.Counter(tuple(sorted((r[1].is_a(), r[2].is_a()))) for r in rows)
    print(f"\nclashes (penetration > {a.tol:g} mm): {len(rows)} element pairs")
    for (c1, c2), n in by_cls.most_common(15):
        print(f"  {n:5d}  {c1} x {c2}")
    if same:
        print(f"  ({len(same)} of them are two elements of the same run overlapping, usually at a joint or bend: "
              "end segments where they meet, or model a fitting, unless the task allows the overlap)")
    for d, x, y, p in rows[:a.limit]:
        print(f"  {d:7.1f} mm  {label(x)}  x  {label(y)}  near ({p[0]:.0f}, {p[1]:.0f}, {p[2]:.0f})")

    if a.clearance:
        same_s = [r for r in soft if net_of.get(r[2].id()) and net_of.get(r[2].id()) == net_of.get(r[3].id())]
        other = [r for r in soft if r not in same_s]
        print(f"\nclearance violations: {len(other)} pairs from different runs or elements closer than the required"
              " clearance" + (f" (plus {len(same_s)} within one run, its own joints or drops, not counted)" if same_s else ""))
        for d, g, x, y, p in sorted(other, key=lambda r: r[0])[:a.limit]:
            print(f"  {d:7.1f} mm < {g:g} mm  {label(x)}  x  {label(y)}  near ({p[0]:.0f}, {p[1]:.0f}, {p[2]:.0f})")
    report_through_voids(f, elems, boxes, net_of, {tuple(sorted((r[1].id(), r[2].id()))) for r in rows}, a.tol, a.limit)
    if a.allowance > 0 and net_of:
        report_close(tree, elems, net_of, a.allowance, {tuple(sorted((r[1].id(), r[2].id()))) for r in rows}, a.limit)
    pts = [np.array([float(v) for v in s.split(",")]) for s in a.point]
    print(f"\nnetworks (elements whose boxes touch within {a.gap:g} mm; grouped by system or class+ObjectType):")
    broken = 0
    for g, comps in nets.items():
        n = sum(len(c) for c in comps)
        types = sorted({f"{f.by_id(i).is_a()}.{getattr(f.by_id(i), 'PredefinedType', None) or '-'}" for c in comps for i in c})
        print(f"  {g}: {n} elements in {len(comps)} network(s)" + ("" if len(comps) == 1 else "  <- MORE THAN ONE NETWORK: a break unless separate circuits are intended")
              + f"  [{', '.join(types[:4])}]")
        broken += len(comps) > 1
        for n_c, c in enumerate(comps[:6], 1):
            cl = np.array([boxes[i][0] for i in c]).min(0)
            ch = np.array([boxes[i][1] for i in c]).max(0)
            extra = ""
            for k, p in enumerate(pts):
                if len(p) == 2:  # plan point: distance in plan and the network's elevation range near it
                    near = [i for i in c if box_dist((boxes[i][0][:2], boxes[i][1][:2]), p) < 1000.0]
                    d2 = min(box_dist((boxes[i][0][:2], boxes[i][1][:2]), p) for i in c)
                    zr = (f"z {min(boxes[i][0][2] for i in near):.0f}..{max(boxes[i][1][2] for i in near):.0f} (extent of the elements within 1 m)"
                          if near else "nothing within 1 m")
                    extra += f"; plan point {k + 1}: {d2:.0f} mm away, {zr}"
                else:
                    extra += f"; {min(box_dist(boxes[i], p) for i in c):.0f} mm from point {k + 1}"
            print(f"     #{n_c}: {len(c):4d} elements, x {cl[0]:.0f}..{ch[0]:.0f} y {cl[1]:.0f}..{ch[1]:.0f} "
                  f"z {cl[2]:.0f}..{ch[2]:.0f}{extra}")
    nsoft = len([r for r in soft if not (net_of.get(r[2].id()) and net_of.get(r[2].id()) == net_of.get(r[3].id()))]) if a.clearance else 0
    print(f"\nsummary: {n_invalid} validation issue(s), {len(rows)} clashing pairs, "
          + (f"{nsoft} clearance violations, " if a.clearance else "") + f"{broken} broken network group(s)")
    return 1 if rows or broken or n_invalid or nsoft else 0


if __name__ == "__main__":
    sys.exit(main())
