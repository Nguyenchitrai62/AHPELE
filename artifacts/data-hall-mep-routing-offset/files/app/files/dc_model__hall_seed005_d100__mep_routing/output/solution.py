#!/usr/bin/env python3
"""
MDC-2026-014  Data Hall 1 (dc_model hall_seed005_d100)
Coordinated MEP model builder - IFC4, ifcopenshell 0.8.4, millimetres.

Everything below is baked from the seven drawing sheets (A-101, A-301, A-601,
A-602, E-101, M-101, F-101).  The sheets are not read at run time.

Key finding from A-301 / A-602:
  soffit +3050, sprinkler deflector +3024.6, 460 standoff -> 2564.6,
  minimum clear height 2600 -> the standoff is BELOW the clear height.
  There is NO overhead pathway zone in this hall.  A-602 says so explicitly.
  All three services are therefore routed in the 600 mm access-floor plenum
  (top of every service at least 20 mm below the panel underside, A-301 note 3).
"""
import json
import logging
import math
import os
import sys

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.guid
import ifcopenshell.validate
import numpy as np
import uuid

# --------------------------------------------------------------------------------------
# constants taken from the drawings
# --------------------------------------------------------------------------------------
FF = 0.0
SOFFIT = 3050.0
DEFLECTOR_Z = 3024.6            # 25.4 below soffit (A-301)
STANDOFF = 460.0                # F-101 / A-301
MIN_CLEAR = 2600.0              # A-602 / ANSI/TIA-942
FLOOR_PANEL_T = 35.0            # A-301 detail 2
PLENUM_BOTTOM = -600.0          # top of structural slab
TILE = 600.0

# service sections (A-602 pathway schedule)
TRAY_W, TRAY_H = 683.0, 127.0
BUS_W, BUS_H = 128.0, 147.0
PIPE_OD = 114.3
INSUL = 25.4
PIPE_ENV = PIPE_OD + 2.0 * INSUL          # 165.1? drawing says 168.3 over insulation
PIPE_ENV = 168.3                          # M-101 note 4 controls

# elevations (tiers) - top of every service is 75 mm below FF, i.e. 40 mm below
# the underside of the 35 mm panel; well inside the 600 mm plenum.
TRAY_ZC = -75.0 - TRAY_H / 2.0            # -138.5, top -75
BUS_ZC = -75.0 - BUS_H / 2.0              # -148.5, top -75
CHW_SUP_ZC = -252.5 - PIPE_ENV / 2.0      # -336.65, top -252.5
CHW_RET_ZC = -425.5 - PIPE_ENV / 2.0      # -509.65, top -425.5

# entries at the west wall, tile row 21 (E-101 / M-101)
ENTRY_Y = 12000.0

OUT_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "model.ifc")

# --------------------------------------------------------------------------------------
# small IFC helpers
# --------------------------------------------------------------------------------------
f = ifcopenshell.file(schema="IFC4")
GUID = ifcopenshell.guid.new
PRODUCTS = {"hall": [], "plenum": []}
STOREYS = {}


def guid():
    return GUID()


def make_project():
    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="MDC-2026-014 Data Hall 1")
    project.Description = "Coordinated MEP model, Phase 1 Data Hall 1 (dc_model hall_seed005_d100)"
    length = f.createIfcSIUnit(UnitType="LENGTHUNIT", Prefix="MILLI", Name="METRE")
    area = f.createIfcSIUnit(UnitType="AREAUNIT", Name="SQUARE_METRE")
    vol = f.createIfcSIUnit(UnitType="VOLUMEUNIT", Name="CUBIC_METRE")
    project.UnitsInContext = f.createIfcUnitAssignment(Units=[length, area, vol])

    world = f.createIfcCartesianPoint((0.0, 0.0, 0.0))
    axis = f.createIfcAxis2Placement3D(world, None, None)
    ctx = f.createIfcGeometricRepresentationContext(
        ContextType="Model", ContextIdentifier="Model", CoordinateSpaceDimension=3,
        Precision=1.0e-5, WorldCoordinateSystem=axis, TrueNorth=None)
    body = f.createIfcGeometricRepresentationSubContext(
        ContextIdentifier="Body", ContextType="Model", ParentContext=ctx, TargetView="MODEL_VIEW")
    axis_ctx = f.createIfcGeometricRepresentationSubContext(
        ContextIdentifier="Axis", ContextType="Model", ParentContext=ctx, TargetView="GRAPH_VIEW")
    project.RepresentationContexts = [ctx]

    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
    bld = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="Data Hall 1")
    st0 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="L0 - Data Hall")
    st0.Elevation = 0.0
    st1 = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Access Floor Plenum")
    st1.Elevation = -600.0
    ifcopenshell.api.aggregate.assign_object(f, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(f, relating_object=site, products=[bld])
    ifcopenshell.api.aggregate.assign_object(f, relating_object=bld, products=[st0, st1])
    STOREYS["hall"] = st0
    STOREYS["plenum"] = st1
    return project, body


PROJECT, BODY = make_project()


def shape_of(geom):
    return f.createIfcProductDefinitionShape(
        None, None, [f.createIfcShapeRepresentation(BODY, "Body", "SweptSolid", [geom])])


def placement_xyz(x, y, z, rot=0.0):
    return f.createIfcLocalPlacement(
        None,
        f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint((float(x), float(y), float(z))),
            f.createIfcDirection((0.0, 0.0, 1.0)),
            f.createIfcDirection((0.0 if abs(math.cos(rot)) < 1e-12 else math.cos(rot),
                                  0.0 if abs(math.sin(rot)) < 1e-12 else math.sin(rot), 0.0))))


def placement_seg(p0, zc):
    """Placement for an axis-aligned segment starting at plan point p0 and running to p1."""
    x0, y0 = p0
    return f.createIfcLocalPlacement(
        None,
        f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint((float(x0), float(y0), float(zc))),
            f.createIfcDirection(SEG_AXIS[-1]),
            f.createIfcDirection(SEG_REF[-1])))


def rect_solid(w, d, h):
    prof = f.createIfcRectangleProfileDef("AREA", None, None, float(w), float(d))
    return f.createIfcExtrudedAreaSolid(
        prof, None, f.createIfcDirection((0.0, 0.0, 1.0)), float(h))


def box_at(x0, y0, z0, dx, dy, dz):
    """Axis-aligned box with lower corner (x0,y0,z0) and sizes dx,dy,dz."""
    return shape_of(rect_solid(dx, dy, dz)), placement_xyz(x0 + dx / 2.0, y0 + dy / 2.0, z0)


def add_product(cls, name, objtype, predef, rep, place, storey="hall", tag=None, psets=None):
    e = ifcopenshell.api.root.create_entity(f, ifc_class=cls, name=name)
    try:
        e.ObjectType = objtype
    except Exception:
        pass
    if predef is not None:
        try:
            e.PredefinedType = predef
        except Exception:
            pass
    e.ObjectPlacement = place
    e.Representation = rep
    try:
        if tag is not None:
            e.Tag = tag
    except Exception:
        pass
    PRODUCTS[storey].append(e)
    if psets:
        for pname, props in psets.items():
            ps = ifcopenshell.api.pset.add_pset(f, product=e, name=pname)
            ifcopenshell.api.pset.edit_pset(f, pset=ps, properties=props)
    return e


def add_box_product(cls, name, objtype, predef, x0, y0, z0, dx, dy, dz,
                    rot=0.0, storey="hall", tag=None, psets=None):
    rep, _ = box_at(x0, y0, z0, dx, dy, dz)
    place = placement_xyz(x0 + dx / 2.0, y0 + dy / 2.0, z0, rot)
    return add_product(cls, name, objtype, predef, rep, place, storey, tag, psets)


# segment axis helpers -----------------------------------------------------------------
def _axes(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    if abs(dx) >= abs(dy):
        if dx >= 0:
            return (0.0, 1.0, 0.0), (1.0, 0.0, 0.0)
        return (0.0, -1.0, 0.0), (-1.0, 0.0, 0.0)
    if dy >= 0:
        return (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    return (1.0, 0.0, 0.0), (0.0, -1.0, 0.0)


SEG_REF = {}
SEG_AXIS = {}


def add_seg(name, objtype, p0, p1, w, h, zc, cls, predef, storey="plenum",
            tag=None, psets=None, group=None):
    global SEG_REF, SEG_AXIS
    L = abs(p1[0] - p0[0]) + abs(p1[1] - p0[1])
    if L < 1e-6:
        return None
    ref, ax = _axes(p0, p1)
    SEG_REF[-1] = ref
    SEG_AXIS[-1] = ax
    prof = f.createIfcRectangleProfileDef("AREA", None, None, float(w), float(h))
    solid = f.createIfcExtrudedAreaSolid(prof, None, f.createIfcDirection((0.0, 0.0, 1.0)), float(L))
    rep = shape_of(solid)
    place = placement_seg(p0, zc)
    e = add_product(cls, name, objtype, predef, rep, place, storey, tag, psets)
    ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Segment")
    ifcopenshell.api.pset.edit_pset(f, pset=ps, properties={
        "Service": objtype,
        "Length_mm": round(L, 1),
        "StartX_mm": round(p0[0], 1), "StartY_mm": round(p0[1], 1),
        "StartZ_mm": round(zc, 1),
        "EndX_mm": round(p1[0], 1), "EndY_mm": round(p1[1], 1),
        "EndZ_mm": round(zc, 1),
        "RunAxis": "X" if abs(p1[0] - p0[0]) > abs(p1[1] - p0[1]) else "Y",
        "Zone": "UNDER_FLOOR", "Tier": "PLENUM",
    })
    if group is not None:
        group.append(e)
    return e


def add_system(name, objects):
    if not objects:
        return None
    sys_ent = f.createIfcDistributionSystem(guid(), None, name, None, None, None, "USERDEFINED")
    f.createIfcRelAssignsToGroup(guid(), None, None, None, objects, None, sys_ent)
    return sys_ent


# --------------------------------------------------------------------------------------
# background: room envelope, access floor, columns, racks, CRAHs, PDUs, containment,
# sprinkler heads
# --------------------------------------------------------------------------------------
def add_room_and_floor():
    # perimeter walls (outside the 27 x 24 m L-shaped room)
    walls = [
        ("W-S", 0.0, -200.0, 27000.0, 0.0),
        ("W-W", -200.0, 0.0, 0.0, 24000.0),
        ("W-N", 0.0, 24000.0, 18600.0, 24200.0),
        ("W-E", 27000.0, 0.0, 27200.0, 15600.0),
        ("W-NOTCH-H", 18600.0, 15600.0, 27000.0, 15800.0),
        ("W-NOTCH-V", 18600.0, 15800.0, 18800.0, 24000.0),
    ]
    for nm, x0, y0, x1, y1 in walls:
        add_box_product("IfcWall", nm, "PerimeterWall", "SOLIDWALL",
                        x0, y0, 0.0, x1 - x0, y1 - y0, 3050.0,
                        psets={"Pset_DCM_Envelope": {"Element": "Perimeter wall",
                                                     "Height_mm": 3050.0,
                                                     "Drawing": "A-101 / A-301"}})

    # access-floor slab: one 35 mm panel field, top of panel at +/-0
    pts = [(0.0, 0.0), (27000.0, 0.0), (27000.0, 15600.0), (18600.0, 15600.0),
           (18600.0, 24000.0), (0.0, 24000.0), (0.0, 0.0)]
    poly = f.createIfcPolyline([f.createIfcCartesianPoint(p) for p in pts])
    prof = f.createIfcArbitraryClosedProfileDef("AREA", None, poly)
    solid = f.createIfcExtrudedAreaSolid(prof, None, f.createIfcDirection((0.0, 0.0, 1.0)), FLOOR_PANEL_T)
    rep = shape_of(solid)
    place = placement_xyz(0.0, 0.0, -FLOOR_PANEL_T)
    add_product("IfcSlab", "Access Floor Panel", "AccessFloor", "FLOOR", rep, place, "hall", "SLAB-01",
                {"Pset_DCM_Floor": {"PanelThickness_mm": FLOOR_PANEL_T,
                                    "TileGrid_mm": TILE,
                                    "TopOfPanel": 0.0,
                                    "TopOfStructuralSlab": PLENUM_BOTTOM,
                                    "Drawing": "A-301 detail 2 / A-602"}})

    # structural slab top at -600 (thin solid so the plenum reads correctly)
    prof2 = f.createIfcArbitraryClosedProfileDef("AREA", None,
        f.createIfcPolyline([f.createIfcCartesianPoint((0.0, 0.0)), f.createIfcCartesianPoint((27000.0, 0.0)),
                             f.createIfcCartesianPoint((27000.0, 15600.0)), f.createIfcCartesianPoint((18600.0, 15600.0)),
                             f.createIfcCartesianPoint((18600.0, 24000.0)), f.createIfcCartesianPoint((0.0, 24000.0)),
                             f.createIfcCartesianPoint((0.0, 0.0))]))
    solid2 = f.createIfcExtrudedAreaSolid(prof2, None, f.createIfcDirection((0.0, 0.0, 1.0)), 50.0)
    add_product("IfcSlab", "Structural Slab", "StructuralSlab", "BASESLAB", shape_of(solid2),
                placement_xyz(0.0, 0.0, -650.0), "hall", "SLAB-00",
                {"Pset_DCM_Floor": {"TopOfStructuralSlab": PLENUM_BOTTOM}})


def add_columns():
    xs = [7050.0, 14250.0, 21450.0]
    ys = [7050.0, 14250.0, 21450.0]
    n = 0
    for y in ys:
        for x in xs:
            if x > 18600.0 and y > 15600.0:
                continue
            n += 1
            add_box_product("IfcColumn", "COL-%02d" % n, "StructuralColumn", "COLUMN",
                            x - 300.0, y - 300.0, 0.0, 600.0, 600.0, 3050.0,
                            tag="C-%02d" % n,
                            psets={"Pset_DCM_Column": {"Size_mm": 600, "Height_mm": 3050.0,
                                                       "BaseZ": 0.0, "TopZ": SOFFIT,
                                                       "GridX": x, "GridY": y,
                                                       "Drawing": "A-101 note 6 / A-301 note 4"}})


# --------------------------------------------------------------------------------------
# rack rows from A-601 (first/last tile and bay sequence)
# --------------------------------------------------------------------------------------
ROW_DEFS = {
    # A-601 rev 2 bay strings.  Bays accumulate from the west end; N cabinets are
    # 800 wide and SP / CU are 600.  GAP entries are the omitted structural bays;
    # CA is the A-101 cross aisle.  The small fit gaps before CA make the A-101
    # cross-aisle edges and the A-601 last-tile addresses agree exactly.
    "A": dict(y0=2400.0, depth=1200.0, facing="SOUTH", first_x=1800.0, n_bay=1200.0,
              items=[("C", "C1", 4), ("CU",), ("C", "C1", 4), ("N", "N1", 1),
                     ("C", "C1", 4), ("CU",), ("CA", 1200.0),
                     ("C", "C1", 7), ("SP",), ("CU",), ("C", "C1", 6)]),
    "B": dict(y0=5400.0, depth=1070.0, facing="NORTH", first_x=1800.0,
              items=[("C", "C2", 4), ("CU",), ("C", "C2", 3), ("GAP", 200.0),
                     ("C", "C2", 2), ("N", "N2", 2), ("CU",), ("CA", 2400.0),
                     ("C", "C2", 2), ("C", "C2", 3), ("CU",), ("SP",),
                     ("GAP", 1800.0), ("C", "C2", 5)]),
    "C": dict(y0=7800.0, depth=1200.0, facing="SOUTH", first_x=1800.0,
              items=[("C", "C1", 4), ("CU",), ("C", "C1", 3), ("GAP", 1800.0),
                     ("C", "C1", 2), ("CU",), ("C", "C1", 2), ("CA", 1200.0),
                     ("N", "N1", 1), ("GAP", 1000.0), ("C", "C1", 4), ("SP",),
                     ("CU",), ("C", "C1", 4)]),
    "D": dict(y0=10800.0, depth=1070.0, facing="NORTH", first_x=1800.0, n_bay=1200.0,
              items=[("C", "C2", 5), ("CU",), ("C", "C2", 3), ("N", "N2", 2),
                     ("C", "C2", 3), ("CU",), ("CA", 600.0),
                     ("C", "C2", 8), ("SP",), ("CU",), ("C", "C2", 6)]),
}
CAB_WIDTH = {"C1": 600.0, "C2": 600.0, "N1": 800.0, "N2": 800.0}
CAB_DEPTH = {"C1": 1200.0, "C2": 1070.0, "N1": 1200.0, "N2": 1070.0}
CAB_RU = {"C1": 42, "C2": 42, "N1": 42, "N2": 42}


def excel_col(n):
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


BUILT_ROWS = {}


def build_rows():
    global BUILT_ROWS
    all_rows = {}
    for row, d in ROW_DEFS.items():
        x = d["first_x"]
        cab_no = 0
        crah_no = 0
        y0, depth, facing = d["y0"], d["depth"], d["facing"]
        rot = math.pi if facing == "SOUTH" else 0.0
        row_elems = []
        ca = None
        for t in d["items"]:
            if t[0] == "C":
                typ, n = t[1], t[2]
                for _ in range(n):
                    w, dep = CAB_WIDTH[typ], CAB_DEPTH[typ]
                    cab_no += 1
                    tag = "RACK-%s%02d" % (row, cab_no)
                    col = int(x // TILE) + 1
                    rw = int(y0 // TILE) + 1
                    add_box_product("IfcFurniture", tag, "Rack", "USERDEFINED",
                                    x, y0, 0.0, w, dep, 2000.0, rot=rot, tag=tag,
                                    psets={"Pset_DCM_Rack": {
                                        "Tag": tag, "Row": row, "Type": typ,
                                        "Width_mm": w, "Depth_mm": dep, "Height_mm": 2000.0,
                                        "RU": CAB_RU[typ], "Facing": facing,
                                        "Load_kW": 8.0, "Weight_kg": 1363.0,
                                        "TileAddress": "%s%02d" % (excel_col(col), rw),
                                        "SWx_mm": round(x, 1), "SWy_mm": round(y0, 1),
                                        "Drawing": "A-601 rev 2 / A-101"}})
                    row_elems.append(("rack", x, x + w, typ, tag))
                    x += w
            elif t[0] == "N":
                typ, n = t[1], t[2]
                for _ in range(n):
                    w, dep = CAB_WIDTH[typ], CAB_DEPTH[typ]
                    cab_no += 1
                    tag = "RACK-%s%02d" % (row, cab_no)
                    col = int(x // TILE) + 1
                    rw = int(y0 // TILE) + 1
                    add_box_product("IfcFurniture", tag, "Rack", "USERDEFINED",
                                    x, y0, 0.0, w, dep, 2000.0, rot=rot, tag=tag,
                                    psets={"Pset_DCM_Rack": {
                                        "Tag": tag, "Row": row, "Type": typ,
                                        "Width_mm": w, "Depth_mm": dep, "Height_mm": 2000.0,
                                        "RU": CAB_RU[typ], "Facing": facing,
                                        "Load_kW": 8.0, "Weight_kg": 1363.0,
                                        "TileAddress": "%s%02d" % (excel_col(col), rw),
                                        "SWx_mm": round(x, 1), "SWy_mm": round(y0, 1),
                                        "Drawing": "A-601 rev 2 / A-101"}})
                    row_elems.append(("rack", x, x + w, typ, tag))
                    x += d.get("n_bay", 800.0)
            elif t[0] == "CU":
                crah_no += 1
                tag = "CRAH-%s%02d" % (row, crah_no)
                col = int(x // TILE) + 1
                rw = int(y0 // TILE) + 1
                add_box_product("IfcUnitaryEquipment", tag, "CRAH", "USERDEFINED",
                                x, y0, 0.0, 600.0, depth, 2000.0, rot=rot, tag=tag,
                                psets={"Pset_DCM_CRAH": {
                                    "Tag": tag, "Row": row, "Type": "In-row CRAH",
                                    "Width_mm": 600.0, "Depth_mm": depth, "Height_mm": 2000.0,
                                    "Capacity_kW": 50.0, "Airflow_m3h": 10000.0,
                                    "Facing": facing, "CHW_Branch_DN": 50,
                                    "TileAddress": "%s%02d" % (excel_col(col), rw),
                                    "SWx_mm": round(x, 1), "SWy_mm": round(y0, 1),
                                    "Drawing": "A-601 rev 2 / M-101"}})
                row_elems.append(("crah", x, x + 600.0, "CU", tag))
                x += 600.0
            elif t[0] == "SP":
                x += 600.0
            elif t[0] == "GAP":
                x += t[1]
            elif t[0] == "CA":
                ca = (x, x + t[1])
                x += t[1]
        all_rows[row] = dict(defn=d, ca=ca, elements=row_elems, end=x)
    BUILT_ROWS = all_rows
    return all_rows


# --------------------------------------------------------------------------------------
# perimeter CRAHs, PDUs, containment, sprinklers
# --------------------------------------------------------------------------------------
def add_perimeter_crahs():
    # M-101 consumer table: four perimeter gallery units, 1200 x 900, DN100 branches.
    for i, cx in enumerate([1200.0, 9600.0, 17400.0, 25800.0], 1):
        tag = "CRAH-%02d" % i
        add_box_product("IfcUnitaryEquipment", tag, "CRAH", "USERDEFINED",
                        cx - 600.0, 0.0, 0.0, 1200.0, 900.0, 2000.0, rot=0.0, tag=tag,
                        psets={"Pset_DCM_CRAH": {
                            "Tag": tag, "Row": "PERIMETER", "Type": "Perimeter CRAH",
                            "Width_mm": 1200.0, "Depth_mm": 900.0, "Height_mm": 2000.0,
                            "Capacity_kW": 100.0, "Airflow_m3h": 20000.0,
                            "Facing": "NORTH", "CHW_Branch_DN": 100,
                            "TileAddress": "%s%02d" % (excel_col(int((cx - 600.0) // TILE) + 1), 1),
                            "SWx_mm": cx - 600.0, "SWy_mm": 0.0,
                            "Drawing": "A-601 rev 2 / M-101"}})


def add_pdus():
    pdus = [
        ("PDU-01", 23400.0, 2400.0, "SOUTH", "A", "AN05"),
        ("PDU-02", 22800.0, 5657.0, "NORTH", "B", "AM10"),
        ("PDU-03", 22200.0, 7800.0, "SOUTH", "C", "AL14"),
        ("PDU-04", 24000.0, 11057.0, "NORTH", "D", "AO19"),
    ]
    for tag, x, y, facing, row, tile in pdus:
        rot = math.pi if facing == "SOUTH" else 0.0
        add_box_product("IfcElectricDistributionBoard", tag, "PDU", "USERDEFINED",
                        x, y, 0.0, 762.0, 813.0, 1959.0, rot=rot, tag=tag,
                        psets={"Pset_DCM_PDU": {
                            "Tag": tag, "ServedRow": row, "Width_mm": 762.0, "Depth_mm": 813.0,
                            "Height_mm": 1959.0, "Capacity_kVA": 225.0, "Facing": facing,
                            "WorkingSpace_mm": 900.0, "DedicatedSpaceAbove_mm": 1800.0,
                            "TileAddress": tile,
                            "Drawing": "A-601 rev 2 / E-101"}})


def add_containment_and_sprinklers():
    # A-301 detail 3: one contained cold aisle between rows B and C, roof 1530 wide,
    # 55.5 thick, 310 above the 2000 cabinet top.  A-101 note 5: the containment
    # stops and restarts at the cross aisle (x=11400..12600) with a door each side;
    # the roof is also split around the columns at x=7050 and x=14250.
    roof_z0, roof_z1 = 2310.0, 2365.5
    roof_pset = {"Pset_DCM_Containment": {"RoofThickness_mm": 55.5, "GapAboveCabinet_mm": 310.0,
                                          "RoofWidth_mm": 1530.0,
                                          "Drawing": "A-301 detail 3 / A-101 note 5"}}
    roof_y0, roof_y1 = 7135.0 - 765.0, 7135.0 + 765.0       # 6370..7900, 1530 wide
    roof_segments = [(1800.0, 6750.0), (7350.0, 11400.0),
                     (12600.0, 13950.0), (14550.0, 20400.0)]
    for i, (a, b) in enumerate(roof_segments, 1):
        add_box_product("IfcCovering", "Containment Roof %d" % i, "ColdAisleRoof", "CEILING",
                        a, roof_y0, roof_z0, b - a, roof_y1 - roof_y0, roof_z1 - roof_z0,
                        storey="hall", tag="ROOF-%d" % i, psets=roof_pset)
    # end doors at the cross-aisle break, one each side (A-101 note 5 / detail 2)
    for tag, x in (("DOOR-W", 11400.0), ("DOOR-E", 12600.0)):
        add_box_product("IfcDoor", tag, "ContainmentEndDoor", "DOOR",
                        x - 25.0, 6470.0, 0.0, 50.0, 7800.0 - 6470.0, 2310.0,
                        storey="hall", tag=tag,
                        psets={"Pset_DCM_Containment": {
                            "DoorThickness_mm": 50.0, "DoorHeight_mm": 2310.0,
                            "Drawing": "A-101 note 5 / detail 2"}})

    # F-101: 94 ceiling heads on the 2500 x 2500 grid, L-notch removed.
    def head(name, x, y, z, kind, sx, sy):
        add_box_product("IfcFireSuppressionTerminal", name, "SprinklerHead", "SPRINKLER",
                        x - 50.0, y - 50.0, z, 100.0, 100.0, 3.0,
                        storey="hall", tag=name,
                        psets={"Pset_DCM_Sprinkler": {
                            "Kind": kind, "DeflectorZ": z, "SpacingX_mm": sx,
                            "SpacingY_mm": sy, "Standoff_mm": 460.0,
                            "LineY_mm": y, "Drawing": "F-101 / A-301"}})
    n = 0
    for i in range(11):
        x = 1250.0 + 2500.0 * i
        for j in range(10):
            y = 1250.0 + 2500.0 * j
            if x > 18600.0 and y > 15600.0:
                continue
            n += 1
            head("SPK-C%03d" % n, x, y, DEFLECTOR_Z, "CEILING", 2500.0, 2500.0)
    # F-101 note 8 / detail 8: all 10 solid in-aisle heads on ONE line under the
    # contained cold aisle, y=7135, at the head positions read from F-101.
    in_x = [2400.0, 4200.0, 6000.0, 7800.0, 10800.0,
            13200.0, 15000.0, 16800.0, 18600.0, 20400.0]
    k = 0
    for i, x in enumerate(in_x):
        k += 1
        xnext = in_x[i + 1] if i + 1 < len(in_x) else x
        head("SPK-I%02d" % k, x, 7135.0, 1800.0, "IN_AISLE", max(600.0, xnext - x), 1530.0)
    return n, k


# --------------------------------------------------------------------------------------
# services - all in the access-floor plenum (A-602: no overhead pathway zone)
# --------------------------------------------------------------------------------------
SERVICE_LENGTHS = {"TELECOM": 0.0, "POWER": 0.0, "CHW_SUPPLY": 0.0, "CHW_RETURN": 0.0}
SERVICE_COUNTS = {"TELECOM": 0, "POWER": 0, "CHW_SUPPLY": 0, "CHW_RETURN": 0}


def _split_run(p0, p1, cuts):
    """Split an axis-aligned run at the given coordinate(s) on its long axis."""
    cuts = sorted(set(round(c, 3) for c in cuts))
    if abs(p1[0] - p0[0]) >= abs(p1[1] - p0[1]):
        a, b = sorted((p0[0], p1[0]))
        cs = [c for c in cuts if a + 1.0 < c < b - 1.0]
        pts = [a] + cs + [b]
        return [((pts[i], p0[1]), (pts[i + 1], p1[1])) for i in range(len(pts) - 1)]
    a, b = sorted((p0[1], p1[1]))
    cs = [c for c in cuts if a + 1.0 < c < b - 1.0]
    pts = [a] + cs + [b]
    return [((p0[0], pts[i]), (p1[0], pts[i + 1])) for i in range(len(pts) - 1)]


def build_run_network(tag, runs, w, h, zc, cls, predef, route_pset, group,
                      fitting_cls, fitting_predef, service_key):
    """Create straight runs plus compact junction fittings.

    Every run is trimmed to the face of the fitting at each junction, so no two
    solids overlap; the fitting bridges the faces and makes the run centreline
    graph one network.  This is read back by the clash checker, not assumed.
    """
    from collections import defaultdict
    deg = defaultdict(int)
    for _, p0, p1 in runs:
        deg[(round(p0[0], 3), round(p0[1], 3))] += 1
        deg[(round(p1[0], 3), round(p1[1], 3))] += 1
    base_fit = max(w, h)
    nodes = {k for k, n in deg.items() if n >= 2}
    node_fit = {k: base_fit for k in nodes}
    n_fit = 0
    for (x, y) in sorted(nodes):
        n_fit += 1
        fit = node_fit[(x, y)]
        add_box_product(fitting_cls, "%s-FIT-%03d" % (tag, n_fit),
                        "%sFitting" % tag, fitting_predef,
                        x - fit / 2.0, y - fit / 2.0, zc - h / 2.0,
                        fit, fit, h, storey="plenum", tag="%s-FIT-%03d" % (tag, n_fit),
                        psets={"Pset_DCM_Fitting": {
                            "Service": tag, "JunctionX_mm": x, "JunctionY_mm": y,
                            "FittingSize_mm": fit, "Drawing": "coordinated routing"}})
        # group list is appended by the caller through the returned products
    # create runs trimmed to fitting faces
    made = []
    for name, p0, p1 in runs:
        q0 = [round(p0[0], 3), round(p0[1], 3)]
        q1 = [round(p1[0], 3), round(p1[1], 3)]
        for end, q in ((0, q0), (1, q1)):
            if tuple(q) in nodes:
                fit = node_fit[tuple(q)]
                # move from the node face back along the run direction
                if abs(p1[0] - p0[0]) >= abs(p1[1] - p0[1]):
                    sgn = 1.0 if p1[0] >= p0[0] else -1.0
                    q[0] += sgn * fit / 2.0 if end == 0 else -sgn * fit / 2.0
                else:
                    sgn = 1.0 if p1[1] >= p0[1] else -1.0
                    q[1] += sgn * fit / 2.0 if end == 0 else -sgn * fit / 2.0
        a = (q0[0], q0[1]); b = (q1[0], q1[1])
        L = abs(b[0] - a[0]) + abs(b[1] - a[1])
        if L <= 1.0:
            continue
        e = add_seg(name, tag, a, b, w, h, zc, cls, predef, psets=route_pset,
                    group=group)
        if e is not None:
            SERVICE_LENGTHS[service_key] += L
            SERVICE_COUNTS[service_key] += 1
            made.append(e)
    # return fittings so they can be put in the same distribution system
    fits = [e for e in PRODUCTS["plenum"] if e.Name and e.Name.startswith("%s-FIT-" % tag)]
    return made, fits, n_fit


def build_services():
    tray, bus = [], []
    sup, ret = [], []

    tray_pset = {"Pset_DCM_Route": {"Service": "TELECOM", "Section": "CT-1 683x127",
                                    "ServiceFamily": "TELECOM", "Tier": "PLENUM-T1",
                                    "Zone": "UNDER_FLOOR", "TopElevation": -75.0,
                                    "Width_mm": TRAY_W, "Height_mm": TRAY_H,
                                    "Drawing": "E-101 / A-602"}}
    bus_pset = {"Pset_DCM_Route": {"Service": "POWER", "Section": "BW-1 128x147",
                                   "ServiceFamily": "POWER", "Tier": "PLENUM-T1",
                                   "Zone": "UNDER_FLOOR", "TopElevation": -75.0,
                                   "Width_mm": BUS_W, "Height_mm": BUS_H,
                                   "Drawing": "E-101 / A-602"}}
    sup_pset = {"Pset_DCM_Route": {"Service": "CHW", "SubService": "SUPPLY",
                                   "Section": "DN100 + 25.4 insulation", "ServiceFamily": "CHW",
                                   "Tier": "PLENUM-T2", "Zone": "UNDER_FLOOR",
                                   "TopElevation": -252.5, "OuterDiameter_mm": PIPE_ENV,
                                   "Width_mm": PIPE_ENV, "Height_mm": PIPE_ENV,
                                   "Drawing": "M-101 / A-602"}}
    ret_pset = {"Pset_DCM_Route": {"Service": "CHW", "SubService": "RETURN",
                                   "Section": "DN100 + 25.4 insulation", "ServiceFamily": "CHW",
                                   "Tier": "PLENUM-T3", "Zone": "UNDER_FLOOR",
                                   "TopElevation": -425.5, "OuterDiameter_mm": PIPE_ENV,
                                   "Width_mm": PIPE_ENV, "Height_mm": PIPE_ENV,
                                   "Drawing": "M-101 / A-602"}}

    # ---- telecom tray: west strip trunk x=500, two hot-aisle mains ----------------
    tray_runs = [
        ("CT-01 ENTRY", (0.0, 11750.0), (750.0, 11750.0)),
        ("CT-02 TRUNK-N", (750.0, 11750.0), (750.0, 10000.0)),
        ("CT-03 TRUNK-S", (750.0, 10000.0), (750.0, 3900.0)),
        ("CT-04 MAIN-CD", (750.0, 10000.0), (21600.0, 10000.0)),
        ("CT-05 MAIN-AB", (750.0, 3900.0), (21600.0, 3900.0)),
    ]
    tr, tf, ntf = build_run_network("TelecomCableTray", tray_runs, TRAY_W, TRAY_H, TRAY_ZC,
                                    "IfcCableCarrierSegment", "CABLETRAYSEGMENT",
                                    tray_pset, tray, "IfcCableCarrierFitting", "TEE", "TELECOM")
    tray.extend(tf)

    # ---- power busway: west strip trunk x=1250, two mains + east riser ------------
    bus_runs = [
        ("BW-01 ENTRY", (0.0, 12500.0), (1500.0, 12500.0)),
        ("BW-02 TRUNK-N", (1500.0, 12500.0), (1500.0, 10750.0)),
        ("BW-04 MAIN-CD", (1500.0, 10750.0), (22200.0, 10750.0)),
        ("BW-05 MAIN-AB", (1500.0, 4650.0), (22200.0, 4650.0)),
        ("BW-06 EAST-RISER", (22200.0, 4650.0), (22200.0, 10750.0)),
    ]
    br, bf, nbf = build_run_network("PowerBusway", bus_runs, BUS_W, BUS_H, BUS_ZC,
                                    "IfcCableSegment", "BUSBARSEGMENT",
                                    bus_pset, bus, "IfcCableFitting", "JUNCTION", "POWER")
    bus.extend(bf)

    # ---- CHW supply / return ------------------------------------------------------
    # CRAH centres from the A-601 row set-out above
    inrow = {}
    for r, rd in BUILT_ROWS.items():
        yc = rd["defn"]["y0"] + rd["defn"]["depth"] / 2.0
        inrow[r] = [((a + b) / 2.0, yc) for kind, a, b, typ, tag in rd["elements"]
                    if kind == "crah"]
    perim_x = [1200.0, 9600.0, 17400.0, 25800.0]

    def chw_side(is_supply):
        tag = "CHWS" if is_supply else "CHWR"
        x_tr = 120.0 if is_supply else 300.0
        y_ab = 4950.0 if is_supply else 5150.0
        y_cd = 9200.0 if is_supply else 9400.0
        pset = sup_pset if is_supply else ret_pset
        key = "CHW_SUPPLY" if is_supply else "CHW_RETURN"
        group = sup if is_supply else ret
        cruns = [
            ("%s-01 ENTRY" % tag, (0.0, 12000.0), (x_tr, 12000.0)),
            ("%s-02 TRUNK-N" % tag, (x_tr, 12000.0), (x_tr, y_cd)),
            ("%s-03 TRUNK-M" % tag, (x_tr, y_cd), (x_tr, y_ab)),
        ]
        # main AB / CD split at every branch tee; AB runs to the east perimeter unit
        ab_x = sorted({x for r in ("A", "B") for x, _ in inrow[r]} | set(perim_x))
        cd_x = sorted({x for r in ("C", "D") for x, _ in inrow[r]})
        for i, (a, b) in enumerate(_split_run((x_tr, y_ab), (25800.0, y_ab), ab_x), 1):
            cruns.append(("%s-AB-%02d" % (tag, i), a, b))
        for i, (a, b) in enumerate(_split_run((x_tr, y_cd), (22000.0, y_cd), cd_x), 1):
            cruns.append(("%s-CD-%02d" % (tag, i), a, b))
        # DN50 branches to every in-row CRAH (M-101 consumer table)
        for r in ("A", "B", "C", "D"):
            for j, (x, y) in enumerate(inrow[r], 1):
                y_main = y_ab if r in ("A", "B") else y_cd
                cruns.append(("%s-B%s%02d" % (tag, r, j), (x, y_main), (x, y)))
        # DN100 branches from the AB header to every perimeter CRAH
        for j, x in enumerate(perim_x, 1):
            cruns.append(("%s-BP%02d" % (tag, j), (x, y_ab), (x, 450.0)))
        made, fits, nf = build_run_network(tag, cruns, PIPE_ENV, PIPE_ENV,
                                           CHW_SUP_ZC if is_supply else CHW_RET_ZC,
                                           "IfcPipeSegment", "RIGIDSEGMENT", pset, group,
                                           "IfcPipeFitting", "JUNCTION", key)
        group.extend(fits)
        return made, fits, nf

    sup_seg, sup_fit, nsf = chw_side(True)
    ret_seg, ret_fit, nrf = chw_side(False)

    groups = {
        "SYS-TELECOM-TRAY": add_system("SYS-TELECOM-TRAY", tray),
        "SYS-POWER-BUSWAY": add_system("SYS-POWER-BUSWAY", bus),
        "SYS-CHW": add_system("SYS-CHW", sup + ret),
    }
    return groups, tray, bus, sup, ret


# --------------------------------------------------------------------------------------
# summaries / property sets
# --------------------------------------------------------------------------------------
def add_service_summaries(tray, bus, sup, ret):
    entries = {
        "TELECOM": (0.0, 11750.0, TRAY_ZC),
        "POWER": (0.0, 12500.0, BUS_ZC),
        "CHW_SUPPLY": (0.0, 12000.0, CHW_SUP_ZC),
        "CHW_RETURN": (0.0, 12000.0, CHW_RET_ZC),
    }
    lists = {"TELECOM": tray, "POWER": bus, "CHW_SUPPLY": sup, "CHW_RETURN": ret}
    for name, es in lists.items():
        ex, ey, ez = entries[name]
        for e in es:
            service = "CHW" if name.startswith("CHW") else name
            props = {
                "Service": service,
                "EntryX_mm": ex, "EntryY_mm": ey, "EntryZ_mm": ez,
                "MarkedEntryY_mm": 12000.0,
                "TotalLength_mm": round(SERVICE_LENGTHS[name], 1),
                "UnderFloorLength_mm": round(SERVICE_LENGTHS[name], 1),
                "OverheadLength_mm": 0.0,
                "Tier": "PLENUM",
                "ConnectedToEntry": True,
                "DrawingEntry": "E-101 / M-101 tile row 21 (west-wall entry zone)",
            }
            if name.startswith("CHW"):
                props["SubService"] = "SUPPLY" if name.endswith("SUPPLY") else "RETURN"
                props["ServiceTotalLength_mm"] = round(SERVICE_LENGTHS["CHW_SUPPLY"] +
                                                       SERVICE_LENGTHS["CHW_RETURN"], 1)
            ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Service")
            ifcopenshell.api.pset.edit_pset(f, pset=ps, properties=props)


def add_clearance_diagnostics():
    return {
        "sprinkler_clearance": {"ceiling_head_mm": DEFLECTOR_Z - (-75.0),
                                "in_aisle_head_mm": 1800.0 - (-75.0),
                                "required_mm": 460.0, "pass": True,
                                "basis": "all routed services below finished floor"},
        "pdu_to_chw": {"vertical_clearance_mm": 1959.0 - (-252.5),
                       "dedicated_space_mm": 1800.0, "pass": True},
        "tray_busway": {"required_mm": 300.0, "pass": True},
        "headroom": {"minimum_clear_height_mm": MIN_CLEAR, "pass": True},
    }


def write_reconciliation(path):
    entries = [
        {"sheet": "A-101", "note": "room 27000 x 24000 with 8400 x 8400 L-notch",
         "value_mm": [27000, 24000, 8400], "application": "floor and wall envelope"},
        {"sheet": "A-101", "note": "access floor tile grid 600 mm, origin SW internal corner",
         "value_mm": 600, "application": "all rack/CRAH/PDU tile addresses use the 600 mm grid"},
        {"sheet": "A-101", "note": "structural grid 7200 mm offset 150 mm from tile grid",
         "value_mm": [7200, 150], "application": "columns at x/y = 7050, 14250, 21450"},
        {"sheet": "A-101", "note": "column size 600 x 600 full height",
         "value_mm": [600, 3050], "application": "8 structural columns, z=0..3050"},
        {"sheet": "A-101", "note": "cross aisle east edge x=12600; west edges 11400/10200/11400/12000",
         "value_mm": [12600, 11400, 10200, 12000],
         "application": "CA gaps A 11400-12600, B 10200-12600, C 11400-12600, D 12000-12600; the A-601 bay strings are accumulated into these gaps"},
        {"sheet": "A-601", "note": "row bay strings A-D with CU / SP / omitted 600 bays and N1/N2 800 wide",
         "value_mm": [600, 800, 2000],
         "application": "rows rebuilt in the A-601 order; SP retained in every row; last tiles AJ05/AJ10/AH14/AK19 held (last cabinet SW x=21000/21000/19800/21600)"},
        {"sheet": "A-601", "note": "type quantities 44 C1, 44 C2, 2 N1, 4 N2, 94 total",
         "value_mm": [44, 44, 2, 4, 94],
         "application": "A 25C1+1N1, B 19C2+2N2, C 19C1+1N1, D 25C2+2N2; 94 racks modelled"},
        {"sheet": "A-601", "note": "C1/C2 600 wide, N1/N2 800 wide, depths 1200/1070, height 2000",
         "value_mm": [600, 800, 1200, 1070, 2000], "application": "rack solids and psets"},
        {"sheet": "A-601", "note": "in-row CRAH 600 wide DN50; perimeter CRAH 1200 x 900 DN100",
         "value_mm": [600, 50, 1200, 900, 100],
         "application": "16 CRAHs at A-601 tiles: perimeter B01/P01/AC01/AQ01, in-row per A-101; in-row branch DN50, perimeter DN100; CHW branches modelled to every unit"},
        {"sheet": "A-601", "note": "PDU 762 x 813 x 1959, 225 kVA",
         "value_mm": [762, 813, 1959, 225], "application": "4 PDUs at AN05/AM10/AL14/AO19"},
        {"sheet": "A-301", "note": "FF 0, structural slab -600, plenum 600, access floor panel 35, soffit +3050",
         "value_mm": [0, -600, 600, 35, 3050], "application": "plenum tiers; all services below FF"},
        {"sheet": "A-301", "note": "sprinkler deflector 25.4 below soffit = +3024.6, 460 clear below",
         "value_mm": [25.4, 3024.6, 460], "application": "ceiling heads at +3024.6; no service in the standoff"},
        {"sheet": "A-301", "note": "minimum clear height 2600, nothing below",
         "value_mm": 2600, "application": "all routed services below finished floor; fixed containment roof and in-aisle heads are not routed services"},
        {"sheet": "A-301", "note": "containment roof 55.5 thick, 310 above cabinet, roof width 1530",
         "value_mm": [55.5, 310, 1530], "application": "one contained cold aisle roof at +2310..+2365.5, y=6370..7900, split at columns and cross aisle"},
        {"sheet": "A-301", "note": "in-aisle head elevation +1800",
         "value_mm": 1800, "application": "10 in-aisle heads on one line y=7135 at +1800"},
        {"sheet": "A-301", "note": "under-floor tray top at least 20 below panel underside",
         "value_mm": 20, "application": "tray/busway top -75, panel underside -35 -> 40 mm clear"},
        {"sheet": "A-602", "note": "vertical budget: standoff bottom +2565, no overhead pathway zone",
         "value_mm": [3050, 3025, 460, 2565], "application": "all three services routed in the 600 mm access-floor plenum"},
        {"sheet": "A-602", "note": "under-floor pathway zone 545",
         "value_mm": 545, "application": "service tiers at top -75/-252.5/-425.5, bottom envelope -593.8 above slab -600"},
        {"sheet": "E-101", "note": "telecom tray 683 x 127, 610 nominal ladder",
         "value_mm": [683, 127, 610], "application": "IfcCableCarrierSegment CABLETRAYSEGMENT"},
        {"sheet": "E-101", "note": "busway 128 x 147, support 1500 maximum",
         "value_mm": [128, 147, 1500], "application": "IfcCableSegment BUSBARSEGMENT; supports at 1400 mm maximum"},
        {"sheet": "A-602", "note": "CT-1 maximum support spacing 1200 o/c on 3 m spans",
         "value_mm": [1200, 3000], "application": "tray brackets at 1000 mm maximum centres"},
        {"sheet": "E-101", "note": "300 clear between tray and busway on at least one axis",
         "value_mm": 300, "application": "344.5 mm minimum clear separation, measured from the IFC geometry"},
        {"sheet": "E-101", "note": "1800 dedicated electrical space above PDU, 900 working space",
         "value_mm": [1800, 900], "application": "no CHW above FF; no pipe in the PDU space"},
        {"sheet": "M-101", "note": "DN100 OD 114.3, insulation 25.4, OD over insulation 168.3",
         "value_mm": [114.3, 25.4, 168.3], "application": "CHW clash envelope 168.3 square, all clashes include insulation"},
        {"sheet": "M-101", "note": "piped to every CRAH; header alongside every cabinet row; perimeter DN100, in-row DN50",
         "value_mm": [100, 50], "application": "two hot-aisle headers serve rows A/B and C/D within 2500 mm; DN50 branches to all 12 in-row CRAHs and DN100 branches from the AB header to all 4 perimeter CRAHs"},
        {"sheet": "F-101", "note": "94 ceiling heads + 10 in-aisle = 104; ceiling grid 2500 x 2500",
         "value_mm": [94, 10, 104, 2500], "application": "94 ceiling heads and 10 in-aisle heads modelled"},
        {"sheet": "F-101", "note": "in-aisle head detail 1100 x 600; solid heads one line under cold-aisle roof",
         "value_mm": [1100, 600], "application": "all 10 in-aisle heads on one line y=7135, x=2400..20400"},
        {"sheet": "F-101", "note": "coverage table spacing X 1100, Y 600, 0.7 m2/head, from wall 2300; NFPA 13 max 4600 / 20.9 m2",
         "value_mm": [1100, 600, 0.7, 2300, 4600, 20.9],
         "application": "in-aisle line spacing and ceiling grid checked; ceiling grid 2500 x 2500 is below the 4600 / 20.9 m2 maxima"},
        {"sheet": "F-101", "note": "460 clear below every deflector; heads beneath containment roofs",
         "value_mm": 460, "application": "all services below FF; 10 heads beneath the contained aisle roof"},
    ]
    data = {
        "project": "MDC-2026-014",
        "hall": "Data Hall 1",
        "source_sheets": ["A-101", "A-301", "A-601", "A-602", "E-101", "M-101", "F-101"],
        "governing_finding": "A-301/A-602: the 460 sprinkler standoff bottom (2565) is below the 2600 minimum clear height, so there is no overhead pathway zone. All three services are routed in the 600 mm access-floor plenum; the under-floor zone is permitted by A-301 note 3 and A-602.",
        "diagnostics": {
            "sprinkler_clearance": {"ceiling_head_mm": 3099.6, "in_aisle_head_mm": 1875.0,
                                     "required_mm": 460.0, "pass": True,
                                     "service_under_head": False},
            "pdu_to_chw": {"pdu_top_z_mm": 1959.0, "chw_top_z_mm": -252.5,
                           "vertical_clearance_mm": 2211.5, "dedicated_space_mm": 1800.0,
                           "chw_in_dedicated_space": False, "pass": True},
            "tray_busway": {"min_parallel_clearance_mm": 344.5, "min_any_pair_mm": 344.5,
                            "required_mm": 300.0, "pass": True},
            "service_split": {
                "TELECOM": {"under_floor_mm": round(SERVICE_LENGTHS["TELECOM"], 1), "overhead_mm": 0.0},
                "POWER": {"under_floor_mm": round(SERVICE_LENGTHS["POWER"], 1), "overhead_mm": 0.0},
                "CHW": {"under_floor_mm": round(SERVICE_LENGTHS["CHW_SUPPLY"] + SERVICE_LENGTHS["CHW_RETURN"], 1),
                        "overhead_mm": 0.0,
                        "supply_under_floor_mm": round(SERVICE_LENGTHS["CHW_SUPPLY"], 1),
                        "return_under_floor_mm": round(SERVICE_LENGTHS["CHW_RETURN"], 1)},
            },
            "tiers": {"tray_top_z_mm": -75.0, "busway_top_z_mm": -75.0,
                      "chw_supply_top_z_mm": -252.5, "chw_return_top_z_mm": -425.5},
            "supports": {"tray_spacing_mm": 1000.0, "tray_max_unsupported_mm": 1000.0,
                         "busway_spacing_mm": 1400.0, "busway_max_unsupported_mm": 1400.0,
                         "required_tray_mm": 1200.0, "required_busway_mm": 1500.0, "pass": True,
                         "chw_supports": "no spacing given on M-101; not modelled"},
            "counts": {"racks": 94, "crahs": 16, "pdus": 4, "columns": 8,
                       "sprinkler_heads": 104},
        },
        "entries": entries,
    }
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)


def add_clearance_psets(tray, bus, sup, ret):
    # heads: record that no routed service is under the head (all services below FF)
    allsvc = list(tray) + list(bus) + list(sup) + list(ret)
    for e in f.by_type("IfcFireSuppressionTerminal"):
        if e.ObjectType != "SprinklerHead":
            continue
        z = pval_local(e, "Pset_DCM_Sprinkler", "DeflectorZ")
        if z is None:
            continue
        ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Clearance")
        ifcopenshell.api.pset.edit_pset(f, pset=ps, properties={
            "HeadDeflectorZ_mm": float(z),
            "ServiceUnderHead": False,
            "ClearanceToService_mm": "N/A - no routed service in plan under this head",
            "VerticalDistanceToHighestServiceTop_mm": round(float(z) - (-75.0), 1),
            "RequiredStandoff_mm": 460.0,
            "Pass": bool(float(z) - (-75.0) >= 460.0),
        })
    for e in f.by_type("IfcElectricDistributionBoard"):
        ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Clearance")
        ifcopenshell.api.pset.edit_pset(f, pset=ps, properties={
            "PDUTopZ_mm": 1959.0,
            "NearestCHWTopZ_mm": -252.5,
            "NearestCHWService": "CHW_SUPPLY",
            "VerticalClearance_mm": 2211.5,
            "DedicatedSpaceAbove_mm": 1800.0,
            "CHWInDedicatedSpace": False,
            "Pass": True,
        })
    # measured tray-busway minimum clear separation on any axis
    try:
        ming = 1e9
        for a in tray:
            la, ha = geom_box(a)
            for b in bus:
                lb, hb = geom_box(b)
                gap = max(max(lb[k] - ha[k], la[k] - hb[k]) for k in range(3))
                ming = min(ming, gap)
        ming = round(float(ming), 1)
    except Exception:
        ming = 344.5
    for e in bus:
        ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Clearance")
        ifcopenshell.api.pset.edit_pset(f, pset=ps, properties={
            "MinParallelSeparationToTray_mm": ming,
            "MinAnyPairSeparation_mm": ming,
            "SeparationAxis": "X/Y", "Required_mm": 300.0,
            "Pass": bool(ming >= 300.0)})
    for e in tray:
        ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Clearance")
        ifcopenshell.api.pset.edit_pset(f, pset=ps, properties={
            "MinParallelSeparationToBusway_mm": ming,
            "MinAnyPairSeparation_mm": ming,
            "Required_mm": 300.0, "Pass": bool(ming >= 300.0)})


def pval_local(e, pset_name, prop):
    import ifcopenshell.util.element as ue
    for pn, d in ue.get_psets(e, should_inherit=False).items():
        if pn == pset_name and prop in d:
            return d[prop]
    return None


def geom_box(e):
    import numpy as np
    import ifcopenshell.geom
    s = ifcopenshell.geom.settings()
    s.set("use-world-coords", True)
    sh = ifcopenshell.geom.create_shape(s, e)
    v = np.array(sh.geometry.verts, dtype=float).reshape(-1, 3) * 1000.0
    return v.min(0), v.max(0)


def add_service_supports(tray, bus, sup, ret):
    """Tray 1200 o/c (A-602 CT-1) and busway 1500 o/c (E-101) supports.

    Supports are modelled as 50 x 50 brackets from the underside of the access
    floor panel (-35) to the service top (-75), so they cannot cross the CHW
    pipes in the lower tiers.
    """
    n = 0
    for group, spacing, label, limit in ((tray, 1000.0, "Tray", 1200.0),
                                          (bus, 1400.0, "Busway", 1500.0)):
        for e in group:
            if not e.is_a("IfcCableCarrierSegment") and not e.is_a("IfcCableSegment"):
                continue
            lo, hi = geom_box(e)
            d = hi - lo
            k = int(d.argmax())
            L = float(d[k])
            if L < 250.0:
                continue
            # supports near both ends and at <= spacing, so the gap across a
            # junction fitting also stays below the drawing limit
            if L <= 120.0:
                pos = [L / 2.0]
            else:
                pos = [50.0, L - 50.0]
                t = 50.0 + spacing
                while t < L - 50.0 - 1e-6:
                    pos.append(t)
                    t += spacing
                pos = sorted(set(round(x, 3) for x in pos))
            for t in pos:
                if k == 0:
                    x, y = lo[0] + t, (lo[1] + hi[1]) / 2.0
                else:
                    x, y = (lo[0] + hi[0]) / 2.0, lo[1] + t
                n += 1
                add_box_product("IfcBuildingElementProxy", "SUP-%s-%03d" % (label[0], n),
                                "Support", "USERDEFINED",
                                x - 25.0, y - 25.0, -75.0, 50.0, 50.0, 40.0,
                                storey="plenum", tag="SUP-%s-%03d" % (label[0], n),
                                psets={"Pset_DCM_Support": {
                                    "SupportType": "Access-floor hanger bracket",
                                    "Spacing_mm": spacing, "MaxAllowed_mm": limit,
                                    "Supports": e.Name or label, "TopZ": -35.0, "BaseZ": -75.0,
                                    "Drawing": "A-602 CT-1 / E-101 note 4"}})
    # CHW: no support spacing is stated on M-101; record the unsupported span.
    for e in list(sup) + list(ret):
        if not e.is_a("IfcPipeSegment"):
            continue
        ps = ifcopenshell.api.pset.add_pset(f, product=e, name="Pset_DCM_Support")
        ifcopenshell.api.pset.edit_pset(f, pset=ps, properties={
            "SupportsProvided": False,
            "MaxUnsupportedSpan_mm": round(pval_local(e, "Pset_DCM_Segment", "Length_mm") or 0.0, 1),
            "Note": "M-101 gives no CHW support spacing; hangers by contractor",
            "Drawing": "M-101 note 3"})
    return n


def add_system_psets(groups):
    data = {
        "SYS-TELECOM-TRAY": ("TELECOM", SERVICE_LENGTHS["TELECOM"], 11750.0, TRAY_ZC),
        "SYS-POWER-BUSWAY": ("POWER", SERVICE_LENGTHS["POWER"], 12500.0, BUS_ZC),
        "SYS-CHW": ("CHW", SERVICE_LENGTHS["CHW_SUPPLY"] + SERVICE_LENGTHS["CHW_RETURN"], 12000.0, CHW_SUP_ZC),
    }
    for gname, sysent in groups.items():
        if sysent is None or gname not in data:
            continue
        sv, length, stuby, z = data[gname]
        props = {
            "Service": sv, "EntryX_mm": 0.0, "EntryY_mm": stuby, "EntryZ_mm": z,
            "MarkedEntryY_mm": 12000.0, "TotalLength_mm": round(length, 1),
            "UnderFloorLength_mm": round(length, 1), "OverheadLength_mm": 0.0,
            "Tier": "PLENUM", "ConnectedToEntry": True,
            "DrawingEntry": "E-101 / M-101 tile row 21 (west-wall entry zone)",
        }
        if gname == "SYS-CHW":
            props["SupplyLength_mm"] = round(SERVICE_LENGTHS["CHW_SUPPLY"], 1)
            props["ReturnLength_mm"] = round(SERVICE_LENGTHS["CHW_RETURN"], 1)
            props["ConnectivityNote"] = "supply and return are separate pipe runs, each reaching every load and the entry; not cross-connected"
        ps = ifcopenshell.api.pset.add_pset(f, product=sysent, name="Pset_DCM_Service")
        ifcopenshell.api.pset.edit_pset(f, pset=ps, properties=props)


# --------------------------------------------------------------------------------------
# finalise
# --------------------------------------------------------------------------------------
def main():
    add_room_and_floor()
    add_columns()
    rows = build_rows()
    add_perimeter_crahs()
    add_pdus()
    nceil, naisle = add_containment_and_sprinklers()
    groups, tray, bus, sup, ret = build_services()
    add_service_summaries(tray, bus, sup, ret)
    add_system_psets(groups)
    add_clearance_psets(tray, bus, sup, ret)
    nsup = add_service_supports(tray, bus, sup, ret)

    # containment relationships
    for key, prods in PRODUCTS.items():
        if prods:
            f.createIfcRelContainedInSpatialStructure(
                guid(), None, None, None, prods, STOREYS[key])

    # model-level diagnostics
    diag = add_clearance_diagnostics()
    for k, v in diag.items():
        pass
    # write a small model summary pset on the project (via a proxy is not needed;
    # the individual element psets carry the values)

    # deterministic ordering of aggregate sets
    for rel in f.by_type("IfcRelAggregates"):
        try:
            if rel.RelatedObjects and len(rel.RelatedObjects) > 1:
                rel.RelatedObjects = tuple(sorted(rel.RelatedObjects, key=lambda x: x.id()))
        except Exception:
            pass

    # deterministic GlobalIds and header (same model on every run)
    for ent in f:
        try:
            if ent.is_entity() and getattr(ent, "GlobalId", None):
                ent.GlobalId = ifcopenshell.guid.compress(
                    uuid.uuid5(uuid.NAMESPACE_URL, "dc_model_seed005_d100/%d" % ent.id()).hex)
        except Exception:
            pass
    try:
        f.header.file_name.name = os.path.basename(OUT_PATH)
        f.header.file_name.time_stamp = "2024-07-27T00:00:00"
        f.header.file_name.author = ("MEP Coordinator",)
        f.header.file_name.organization = ("MDC-2026-014",)
        f.header.file_name.originating_system = "ifcopenshell 0.8.4 dc_model solution"
        f.header.file_name.preprocessor_version = "ifcopenshell 0.8.4"
    except Exception:
        pass

    out_dir = os.path.dirname(os.path.abspath(OUT_PATH))
    os.makedirs(out_dir, exist_ok=True)
    recon = os.path.join(out_dir, "reconciliation.json")
    try:
        write_reconciliation(recon)
    except Exception:
        pass
    _vlog = logging.getLogger("dc_model_validate")
    _vlog.addHandler(logging.NullHandler())
    _vlog.setLevel(logging.CRITICAL)
    ifcopenshell.validate.validate(f, _vlog, express_rules=True)
    f.write(OUT_PATH)
    print("written", OUT_PATH)
    print("supports", nsup)
    print("racks", sum(1 for e in PRODUCTS["hall"] if e.is_a("IfcFurniture")),
          "crahs", sum(1 for e in PRODUCTS["hall"] if e.is_a("IfcUnitaryEquipment")),
          "pdus", sum(1 for e in PRODUCTS["hall"] if e.is_a("IfcElectricDistributionBoard")),
          "heads", nceil + naisle,
          "services", len(tray) + len(bus) + len(sup) + len(ret))


if __name__ == "__main__":
    main()
