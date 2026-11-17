#!/usr/bin/env python3
"""AHPELE geometry check for IFC models: clashes and network connectivity, read back from the FILE.

  python3 ahpele_clash.py model.ifc                       # validation + clashes (> 2 mm) + connectivity
  python3 ahpele_clash.py model.ifc --tol 2 --gap 5       # penetration tolerance / joint gap, in millimetres
  python3 ahpele_clash.py model.ifc --point 200,4910,3000 # distance from each network to a point (mm, world)
  python3 ahpele_clash.py model.ifc --ignore IfcSlab,IfcCovering   # leave classes out of the clash test
  python3 ahpele_clash.py model.ifc --clearance IfcPipeSegment=25.4  # soft clash: keep 25.4 mm around pipes (insulation,
                                                                   # access or code envelopes the contract counts)

Why: a self-check computed from the script's own variables shows what you MEANT to build; a grader
reads the IFC with ifcopenshell's geometry engine (world coordinates, placements, units, profiles).
This tool does the same, so a wrong unit, a misplaced element or an overlap shows up here.

Validation: ifcopenshell.validate with EXPRESS where-rules (schema-only if the rule engine cannot run), the
check most IFC graders run first; any issue can make the whole file fail.

Clashes: ifcopenshell.geom.tree intersection test between every pair of products with a body
(spaces, openings, annotations and spatial elements are skipped); a pair clashes when one solid
penetrates the other by more than --tol. Elements meant to touch (segments meeting at a joint, a
rack standing on the floor) do not count.

Connectivity: routed elements (pipe / duct / cable-carrier / cable segments and fittings) are
grouped by system (IfcRelAssignsToGroup) or else by class + ObjectType; inside each group, elements
whose bounding boxes touch within --gap form one network. More than one network in a group means a
break. Needs ifcopenshell (and numpy); knows nothing about any particular task.
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
                boxes[shape.id] = (v.min(0), v.max(0))
            if not it.next():
                break
    return f, tree, boxes


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
    out = {}
    for g, ids in sorted(groups.items()):
        lo = np.array([boxes[i][0] for i in ids]) - gap
        hi = np.array([boxes[i][1] for i in ids]) + gap
        parent = list(range(len(ids)))

        def root(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i in range(len(ids)):
            touch = np.all((lo[i] <= hi[i + 1:]) & (lo[i + 1:] <= hi[i]), axis=1)
            for j in np.nonzero(touch)[0] + i + 1:
                parent[root(i)] = root(int(j))
        comps = collections.defaultdict(list)
        for i in range(len(ids)):
            comps[root(i)].append(ids[i])
        out[g] = list(comps.values())
    return out


def validate(path, limit):
    """Schema + EXPRESS where-rule validation, as graders usually run first. Returns the number of issues."""
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


def box_dist(b, p):
    return float(np.linalg.norm(np.maximum(0, np.maximum(b[0] - p, p - b[1]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ifc")
    ap.add_argument("--tol", type=float, default=2.0, help="penetration that counts as a clash, mm (default 2)")
    ap.add_argument("--gap", type=float, default=5.0, help="joint gap that still connects two elements, mm")
    ap.add_argument("--ignore", default="", help="comma-separated classes left out of the clash test")
    ap.add_argument("--point", action="append", default=[], help="x,y,z in mm: report each network's distance")
    ap.add_argument("--clearance", action="append", default=[],
                    help="CLASS=MM: elements of CLASS must stay MM away from every other solid (insulation, envelopes)")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--threads", type=int, default=min(4, multiprocessing.cpu_count()))
    a = ap.parse_args()

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
    rows.sort(key=lambda r: -r[0])
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
    nets = networks(f, boxes, a.gap)
    net_of = {i: g for g, comps in nets.items() for c in comps for i in c}
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
        print(f"\nclearance violations: {len(soft)} pairs closer than the required clearance"
              + (f" ({len(same_s)} within one run, usually joints)" if same_s else ""))
        for d, g, x, y, p in sorted(soft, key=lambda r: r[0])[:a.limit]:
            print(f"  {d:7.1f} mm < {g:g} mm  {label(x)}  x  {label(y)}  near ({p[0]:.0f}, {p[1]:.0f}, {p[2]:.0f})")
    pts = [np.array([float(v) for v in s.split(",")]) for s in a.point]
    print(f"\nnetworks (elements touching within {a.gap:g} mm, grouped by system or class+ObjectType):")
    broken = 0
    for g, comps in nets.items():
        comps.sort(key=len, reverse=True)
        n = sum(len(c) for c in comps)
        print(f"  {g}: {n} elements in {len(comps)} network(s)" + ("" if len(comps) == 1 else "  <- BROKEN"))
        broken += len(comps) > 1
        for c in comps[:6]:
            cl = np.array([boxes[i][0] for i in c]).min(0)
            ch = np.array([boxes[i][1] for i in c]).max(0)
            extra = "".join(f"; {min(box_dist(boxes[i], p) for i in c):.0f} mm from point {k + 1}"
                            for k, p in enumerate(pts))
            print(f"     {len(c):4d} elements, x {cl[0]:.0f}..{ch[0]:.0f} y {cl[1]:.0f}..{ch[1]:.0f} "
                  f"z {cl[2]:.0f}..{ch[2]:.0f}{extra}")
    nsoft = len(soft) if a.clearance else 0
    print(f"\nsummary: {n_invalid} validation issue(s), {len(rows)} clashing pairs, "
          + (f"{nsoft} clearance violations, " if a.clearance else "") + f"{broken} broken network group(s)")
    return 1 if rows or broken or n_invalid or nsoft else 0


if __name__ == "__main__":
    sys.exit(main())
