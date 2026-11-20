"""Coordinated IFC4 model of data hall dc_model hall_seed000_d000.

Self-contained: all values read from the seven drawing sheets are baked in as
literals.  Writes one IFC4 file to sys.argv[1] (default output/model.ifc).

Units: project length unit = millimetre.  All explicit IfcCartesianPoint and
profile dimensions below are in millimetres (the project unit).  No
ifcopenshell.api placement-matrix helper is used, so no metre conversion is
applied anywhere.
"""
import sys, os, re, hashlib, uuid, math, logging

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.validate

# ----------------------------------------------------------------------------
# Drawing-derived constants (millimetres unless noted)
# ----------------------------------------------------------------------------
ROOM_X, ROOM_Y = 27000.0, 21000.0
FF = 0.0
SOFFIT = 3600.0
STRUCT_SLAB_TOP = -900.0
PANEL_T = 35.0
ACCESS_FLOOR_HEIGHT = 900.0
PLENUM_VOID = ACCESS_FLOOR_HEIGHT - PANEL_T   # 865 mm clear void
DEFLECTOR = SOFFIT - 25.4                 # 3574.6  A-301 / F-101
CLEAR_BELOW_DEFLECTOR = 460.0
MIN_HEADROOM = 2600.0
HEADROOM_ZONE_TOP = DEFLECTOR - CLEAR_BELOW_DEFLECTOR  # 3114.6
OVERHEAD_BAND_BOT = 2600.0
OVERHEAD_BAND_TOP = 3114.6
TRAY_W, TRAY_H = 683.0, 127.0             # A-602 CT-1
BUS_W, BUS_H = 128.0, 147.0               # A-602 BW-1
PIPE_OD = 168.3                           # over 25.4 mm insulation, M-101 note 3
PIPE_BARE_OD = 114.3
INSUL_THK = 25.4
PIPE_BRANCH_OD = 60.3 + 2.0 * INSUL_THK  # DN50 row branch envelope = 111.1 mm
TRAY_BUS_SEP = 300.0
PDU_DEDICATED = 1800.0
PDU_HEIGHT = 1959.0
PDU_W, PDU_D = 762.0, 813.0

# accessory bands (chosen to satisfy 2600 <= bottom, top <= 3114.6)
TRAY_Z0 = 2880.0
TRAY_ZC = TRAY_Z0 + TRAY_H / 2.0          # 2943.5
CHW_ZC = 2750.0                           # bottom 2665.85, top 2834.15
CHW_Z0 = CHW_ZC - PIPE_OD / 2.0           # 2665.85
BUS_Z0 = -400.0
BUS_ZC = BUS_Z0 + BUS_H / 2.0             # -226.5

# Tile grid
TILE = 600.0

# Row schedule from A-601 + A-101 (bay sequence, west to east, accumulating)
ROWS = [
    # row, y0 (south edge), facing, sequence
    ("A", 2400.0, "SOUTH", [("C1",4),("CU",1),("C1",3),("N1",1),("C1",3),("CU",1),
                            ("CA",1600.0),("C1",6),("SP",1),("CU",1),("C1",5)]),
    ("B", 5400.0, "NORTH", [("C1",4),("CU",1),("C1",5),("N1",2),("CU",1),
                            ("CA",1400.0),("C1",7),("SP",1),("CU",1),("C1",5)]),
    ("C", 7800.0, "SOUTH", [("C1",3),("CU",1),("C1",6),("GAP",1200.0),("CU",1),
                            ("CA",1600.0),("N1",1),("C1",4),("CU",1),("SP",1),
                            ("C1",1),("GAP",1200.0),("C1",3)]),
    ("D", 10800.0, "NORTH", [("C1",4),("CU",1),("C1",3),("N1",2),("C1",2),("CU",1),
                             ("CA",1400.0),("C1",7),("SP",1),("CU",1),("C1",5)]),
    ("E", 13200.0, "SOUTH", [("C1",4),("CU",1),("C1",5),("N1",1),("C1",1),("CU",1),
                             ("CA",1600.0),("C1",6),("SP",1),("CU",1),("C1",5)]),
    ("F", 16200.0, "NORTH", [("C1",4),("CU",1),("C1",5),("GAP",1200.0),("CU",1),
                             ("CA",1400.0),("N1",2),("C1",5),("SP",1),("GAP",600.0),
                             ("CU",1),("C1",4)]),
]
ROW_DEPTH = 1200.0
ROW_X0 = 1800.0

# Perimeter CRAHs (A-601 tile B01, P01, AC01, AQ01)
PERIM_CRAH = [
    ("CRAH-01", 600.0, 0.0),
    ("CRAH-02", 9000.0, 0.0),
    ("CRAH-03", 16800.0, 0.0),
    ("CRAH-04", 25200.0, 0.0),
]

# PDUs from A-601 (tile address, facing)
PDUS = [
    ("PDU-01", "AJ05", "SOUTH"),
    ("PDU-02", "AK10", "NORTH"),
    ("PDU-03", "AJ14", "SOUTH"),
    ("PDU-04", "AK19", "NORTH"),
    ("PDU-05", "AJ23", "SOUTH"),
    ("PDU-06", "AK28", "NORTH"),
]

# Structural columns: 600 x 600, full clear height, at the structure gaps of
# rows C and F and the free-standing east columns shown on A-101.
COLUMNS = [
    (8100.0, 8100.0), (16200.0, 8100.0), (24900.0, 8100.0),
    (8100.0, 16500.0), (16200.0, 16500.0), (24900.0, 16500.0),
]
COL_W = 600.0
COL_H = 3600.0

# Containment: cold aisles B/C (y 6600..7800) and D/E (y 12000..13200)
# roof width 1400, thickness 55.5, underside 2000, split by the cross aisle.
# The east roof segment runs to the longer row end x=19800; the drawn east
# in-aisle heads at x~19350 are under it (F-101 note 8).
CONTAINMENT = [
    # (x0, x1, y_center)
    (1800.0, 10000.0, 7200.0),
    (11400.0, 19800.0, 7200.0),
    (1800.0, 10000.0, 12600.0),
    (11400.0, 19800.0, 12600.0),
]
CONT_ROOF_W = 1400.0
CONT_ROOF_T = 55.5
CONT_ROOF_Z = 2000.0
CONT_DOOR_T, CONT_DOOR_H = 60.0, 2055.5

# Sprinkler heads
CEIL_HEADS = [(1500.0 + 3000.0*i, 1500.0 + 3000.0*j) for i in range(9) for j in range(7)]
# F-101 note 3: a head interrupted by structure is relocated to the nearest clear
# tile, not omitted.  Only the two heads physically inside a 600 mm column
# footprint ((16500,16500) and (25500,16500)) are relocated, each 600 mm south to
# the nearest clear 600 mm tile.  All other 61 ceiling heads stay on the drawn
# 3000 mm grid.
HEAD_RELOC = {
    (16500.0, 16500.0): (16500.0, 15900.0),
    (25500.0, 16500.0): (25500.0, 15900.0),
}
CEIL_HEADS = [HEAD_RELOC.get((x, y), (x, y)) for x, y in CEIL_HEADS]
# F-101 in-aisle heads, read from the drawn symbols (8 per cold aisle, under the
# containment roof).  They are not on the ceiling 3000 mm grid.
IN_AISLE_HEADS = [(2300.0, 7200.0), (4770.0, 7200.0), (7240.0, 7200.0), (9710.0, 7200.0),
                  (11910.0, 7200.0), (14380.0, 7200.0), (16850.0, 7200.0), (19350.0, 7200.0),
                  (2300.0, 12600.0), (4770.0, 12600.0), (7240.0, 12600.0), (9710.0, 12600.0),
                  (11910.0, 12600.0), (14380.0, 12600.0), (16850.0, 12600.0), (19350.0, 12600.0)]
IN_AISLE_DEFLECTOR = 1890.0

# Services
TRAY_LANES = {"AB": 4150.0, "CD": 9600.0, "EF": 15000.0}
CHW_LANES  = {"AB": 4650.0, "CD": 10150.0, "EF": 15550.0}
BUS_LANES  = {"AB": 4500.0, "CD": 9900.0, "EF": 15300.0}
TRAY_TRUNK_X = 1400.0
CHW_TRUNK_X = 600.0
BUS_TRUNK_X = 1400.0
# Main branches stop at x=16500: rows B/D/F are then served 81.7% and rows
# A/C/E 84.5%, both above the 80% gate with a visible reserve.
MAIN_X1 = 16500.0
BUS_PDU_X1 = 21981.0
CHW_AB_X1 = 25800.0
PERIM_STUB_Y = 2100.0

# ----------------------------------------------------------------------------
# Deterministic ids
# ----------------------------------------------------------------------------
_used = set()
def gid(key):
    k = 0
    base = key
    while key in _used:
        k += 1
        key = "%s#%d" % (base, k)
    _used.add(key)
    digest = hashlib.md5(key.encode("utf-8")).digest()
    return ifcopenshell.guid.compress(str(uuid.UUID(bytes=digest[:16])))

# ----------------------------------------------------------------------------
# IFC skeleton
# ----------------------------------------------------------------------------
f = ifcopenshell.api.run("project.create_file", version="IFC4")
project = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcProject", name="DC Model - Data Hall")
# Deterministic units: millimetre length, square metre area, cubic metre volume.
# (ifcopenshell.api.unit.assign_unit builds a Python set, so its entity order
# varies between runs; create the three SI units explicitly instead.)
_unit_mm = f.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")
_unit_m2 = f.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
_unit_m3 = f.createIfcSIUnit(None, "VOLUMEUNIT", None, "CUBIC_METRE")
project.UnitsInContext = f.createIfcUnitAssignment([_unit_mm, _unit_m2, _unit_m3])
ctx = ifcopenshell.api.run("context.add_context", f, context_type="Model")
body_ctx = ifcopenshell.api.run("context.add_context", f, context_type="Model",
                                context_identifier="Body", target_view="MODEL_VIEW", parent=ctx)
site = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcSite", name="DC Site")
building = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuilding", name="DC Building")
storey = ifcopenshell.api.run("root.create_entity", f, ifc_class="IfcBuildingStorey", name="Level 0 - Data Hall")
rel_site = ifcopenshell.api.run("aggregate.assign_object", f, products=[site], relating_object=project)
rel_bld = ifcopenshell.api.run("aggregate.assign_object", f, products=[building], relating_object=site)
rel_sty = ifcopenshell.api.run("aggregate.assign_object", f, products=[storey], relating_object=building)
# deterministic GlobalIds for the spatial entities created by the API
project.GlobalId = gid("project")
site.GlobalId = gid("site")
building.GlobalId = gid("building")
storey.GlobalId = gid("storey")
for rel, key in ((rel_site, "rel-site"), (rel_bld, "rel-bld"), (rel_sty, "rel-sty")):
    if rel is not None:
        rel.GlobalId = gid(key)
storey.Elevation = 0.0
storey.CompositionType = "ELEMENT"

# ----------------------------------------------------------------------------
# Geometry helpers (all dimensions in project units = mm)
# ----------------------------------------------------------------------------
def pt2(x, y):
    return f.createIfcCartesianPoint((float(x), float(y)))

def pt3(x, y, z):
    return f.createIfcCartesianPoint((float(x), float(y), float(z)))

def dir3(x, y, z):
    return f.createIfcDirection((float(x), float(y), float(z)))

def axis2():
    return f.createIfcAxis2Placement2D(pt2(0.0, 0.0), None)

def rect_profile(w, h):
    return f.createIfcRectangleProfileDef("AREA", None, axis2(), float(w), float(h))

def circ_profile(r):
    return f.createIfcCircleProfileDef("AREA", None, axis2(), float(r))

def body_rep(profile, depth):
    pos = f.createIfcAxis2Placement3D(pt3(0.0, 0.0, 0.0), None, None)
    solid = f.createIfcExtrudedAreaSolid(profile, pos, dir3(0.0, 0.0, 1.0), float(depth))
    rep = f.createIfcShapeRepresentation(body_ctx, "Body", "SweptSolid", [solid])
    return f.createIfcProductDefinitionShape(None, None, [rep])

def placement_xyz(x, y, z, theta_deg=0.0):
    th = math.radians(theta_deg)
    ax = f.createIfcAxis2Placement3D(pt3(x, y, z), dir3(0.0, 0.0, 1.0),
                                     dir3(math.cos(th), math.sin(th), 0.0))
    return f.createIfcLocalPlacement(None, ax)

def placement_run(p0, p1):
    dx, dy, dz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    ux, uy, uz = dx/L, dy/L, dz/L
    if abs(uz) > 0.9:
        ref = (1.0, 0.0, 0.0)
    elif abs(uy) > 0.9:
        ref = (1.0, 0.0, 0.0)
    else:
        ref = (0.0, 1.0, 0.0)
    ax = f.createIfcAxis2Placement3D(pt3(*p0), dir3(ux, uy, uz), dir3(*ref))
    return f.createIfcLocalPlacement(None, ax), L

# ----------------------------------------------------------------------------
# Property sets
# ----------------------------------------------------------------------------
def val(v):
    if isinstance(v, bool):
        return f.createIfcBoolean(v)
    if isinstance(v, int):
        return f.createIfcInteger(v)
    if isinstance(v, float):
        return f.createIfcReal(float(v))
    return f.createIfcLabel(str(v))

def add_pset(el, name, props, key):
    props_list = [f.createIfcPropertySingleValue(k, None, val(v), None)
                  for k, v in props.items() if v is not None]
    ps = f.createIfcPropertySet(gid("pset:"+key+":"+name), None, name, None, props_list)
    f.createIfcRelDefinesByProperties(gid("psetrel:"+key+":"+name), None, None, None, [el], ps)

def decorate(el, key, common, location, specific=None):
    add_pset(el, "Pset_DCM_Common", common, key)
    add_pset(el, "Pset_DCM_Location", location, key)
    if specific:
        for name, props in specific.items():
            add_pset(el, name, props, key)

COMMON_MODEL = {
    "DCM_Project": "dc_model hall_seed000_d000",
    "DCM_Status": "ISSUED FOR CONSTRUCTION - coordination model",
    "DCM_Units": "millimetre",
    "DCM_Source": "A-101 rev2 2026-07-27; A-301 rev2; A-601 rev2; A-602 rev1; E-101 rev2; F-101 rev2; M-101 rev2",
}

# ----------------------------------------------------------------------------
# Equipment
# ----------------------------------------------------------------------------
elements = []

def add_box(cls, name, objtype, predefined, cx, cy, z0, sx, sy, sz, theta,
            tag, key, common_extra=None, loc_extra=None, specific=None):
    rep = body_rep(rect_profile(sx, sy), sz)
    pl = placement_xyz(cx, cy, z0, theta)
    if cls == "IfcFurniture":
        el = f.createIfcFurniture(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    elif cls == "IfcColumn":
        el = f.createIfcColumn(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    elif cls == "IfcSlab":
        el = f.createIfcSlab(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    elif cls == "IfcCovering":
        el = f.createIfcCovering(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    elif cls == "IfcBuildingElementProxy":
        el = f.createIfcBuildingElementProxy(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    elif cls == "IfcElectricDistributionBoard":
        el = f.createIfcElectricDistributionBoard(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    elif cls == "IfcEnergyConversionDevice":
        el = f.createIfcEnergyConversionDevice(gid(key), None, name, None, objtype, pl, rep, tag)
    elif cls == "IfcFireSuppressionTerminal":
        el = f.createIfcFireSuppressionTerminal(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    else:
        raise ValueError(cls)
    common = dict(COMMON_MODEL); common.update(common_extra or {})
    loc = {"DCM_X_mm": float(cx), "DCM_Y_mm": float(cy), "DCM_Z_mm": float(z0)}
    loc.update(loc_extra or {})
    decorate(el, key, common, loc, specific)
    elements.append(el)
    return el

def add_cyl(cls, name, objtype, predefined, x, y, z0, radius, height, tag, key,
            common_extra=None, loc_extra=None, specific=None):
    rep = body_rep(circ_profile(radius), height)
    pl = placement_xyz(x, y, z0, 0.0)
    if cls == "IfcFireSuppressionTerminal":
        el = f.createIfcFireSuppressionTerminal(gid(key), None, name, None, objtype, pl, rep, tag, predefined)
    else:
        raise ValueError(cls)
    common = dict(COMMON_MODEL); common.update(common_extra or {})
    loc = {"DCM_X_mm": float(x), "DCM_Y_mm": float(y), "DCM_Z_mm": float(z0)}
    loc.update(loc_extra or {})
    decorate(el, key, common, loc, specific)
    elements.append(el)
    return el

# tile address helpers --------------------------------------------------------
def col_letters(n):
    s = ""
    while n > 0:
        n, r = divmod(n-1, 26)
        s = chr(65+r) + s
    return s

def tile_address(x, y):
    col = int(math.floor(x / TILE)) + 1
    row = int(math.floor(y / TILE)) + 1
    return "%s%02d" % (col_letters(col), row)

def tile_to_xy(addr):
    m = re.match(r"^([A-Z]+)(\d+)$", addr)
    letters, num = m.group(1), int(m.group(2))
    n = 0
    for ch in letters:
        n = n*26 + (ord(ch)-64)
    return (n-1)*TILE, (num-1)*TILE

# Racks / in-row CRAHs by accumulating the bay sequence ----------------------
rack_count = 0
crah_count = 0
row_bays = {}
for rname, y0, facing, seq in ROWS:
    x = ROW_X0
    cab_no = 0
    crah_no = 0
    theta = 0.0 if facing == "SOUTH" else 180.0
    bays = []
    for typ, n in seq:
        if typ in ("C1", "N1"):
            w = 600.0 if typ == "C1" else 800.0
            for k in range(n):
                cab_no += 1
                rack_count += 1
                tag = "RACK-%s%02d" % (rname, cab_no)
                cx, cy = x + w/2.0, y0 + ROW_DEPTH/2.0
                spec = {
                    "Pset_DCM_Equipment": {
                        "DCM_EquipmentType": "Server Cabinet" if typ == "C1" else "Distributor Cabinet",
                        "DCM_CabinetType": typ,
                        "Width_mm": w, "Depth_mm": 1200.0, "Height_mm": 2000.0,
                        "RU": 42, "Load_kg": 1363.0, "kW_per_cabinet": 8.0,
                        "FrontFaces": facing, "Row": rname,
                    },
                    "Pset_DCM_Rack": {
                        "DCM_Tag": tag, "DCM_Row": rname, "DCM_CabinetType": typ,
                        "DCM_Tile": tile_address(x, y0), "DCM_Width_mm": w,
                        "DCM_Depth_mm": 1200.0, "DCM_Height_mm": 2000.0, "DCM_RU": 42,
                        "DCM_Load_kg": 1363.0, "DCM_kW": 8.0, "DCM_FrontFaces": facing,
                    },
                }
                add_box("IfcFurniture", tag, "Rack", "USERDEFINED",
                        cx, cy, 0.0, w, ROW_DEPTH, 2000.0, theta, tag, "rack:"+tag,
                        common_extra={"DCM_Category": "Rack", "DCM_Tag": tag},
                        loc_extra={"DCM_Row": rname, "DCM_Tile": tile_address(x, y0),
                                   "DCM_Facing": facing, "DCM_Width_mm": w,
                                   "DCM_Depth_mm": 1200.0},
                        specific=spec)
                bays.append((tag, x, w, "RACK"))
                x += w
        elif typ == "CU":
            crah_no += 1
            crah_count += 1
            tag = "CRAH-%s%02d" % (rname, crah_no)
            cx, cy = x + 300.0, y0 + ROW_DEPTH/2.0
            spec = {
                "Pset_DCM_Equipment": {
                    "DCM_EquipmentType": "In-row CRAH", "Width_mm": 600.0,
                    "Depth_mm": 1200.0, "Height_mm": 2000.0,
                    "Capacity_kW": 50.0, "Airflow_m3h": 9000.0, "CHW_DN": 50,
                    "FrontFaces": facing, "Row": rname,
                },
                "Pset_DCM_CRAH": {
                    "DCM_Tag": tag, "DCM_Row": rname, "DCM_CRAHType": "In-row",
                    "DCM_Tile": tile_address(x, y0), "DCM_Width_mm": 600.0,
                    "DCM_Depth_mm": 1200.0, "DCM_Height_mm": 2000.0,
                    "DCM_Capacity_kW": 50.0, "DCM_Airflow_m3h": 9000.0,
                    "DCM_CHW_DN": 50, "DCM_FrontFaces": facing,
                },
            }
            add_box("IfcEnergyConversionDevice", tag, "CRAH", "USERDEFINED",
                    cx, cy, 0.0, 600.0, ROW_DEPTH, 2000.0, theta, tag, "crah:"+tag,
                    common_extra={"DCM_Category": "CRAH", "DCM_Tag": tag},
                    loc_extra={"DCM_Row": rname, "DCM_Tile": tile_address(x, y0),
                               "DCM_Facing": facing},
                    specific=spec)
            bays.append((tag, x, 600.0, "CRAH"))
            x += 600.0
        elif typ == "CA":
            x += n
        elif typ == "SP":
            x += 600.0
        elif typ == "GAP":
            x += n
        else:
            raise ValueError(typ)
    row_bays[rname] = (bays, x - ROW_X0)

# Perimeter CRAHs -------------------------------------------------------------
for tag, x0, y0 in PERIM_CRAH:
    cx, cy = x0 + 600.0, y0 + 450.0
    add_box("IfcEnergyConversionDevice", tag, "CRAH", "USERDEFINED",
            cx, cy, 0.0, 1200.0, 900.0, 2000.0, 0.0, tag, "pcrah:"+tag,
            common_extra={"DCM_Category": "CRAH", "DCM_Tag": tag},
            loc_extra={"DCM_Row": "PERIMETER", "DCM_Tile": tile_address(x0, y0),
                       "DCM_Facing": "SOUTH"},
            specific={"Pset_DCM_Equipment": {
                "DCM_EquipmentType": "Perimeter CRAH", "Width_mm": 1200.0,
                "Depth_mm": 900.0, "Height_mm": 2000.0, "Capacity_kW": 100.0,
                "Airflow_m3h": 20000.0, "CHW_DN": 100, "FrontFaces": "SOUTH",
                "Row": "PERIMETER"},
                "Pset_DCM_CRAH": {
                    "DCM_Tag": tag, "DCM_Row": "PERIMETER", "DCM_CRAHType": "Perimeter",
                    "DCM_Tile": tile_address(x0, y0), "DCM_Width_mm": 1200.0,
                    "DCM_Depth_mm": 900.0, "DCM_Height_mm": 2000.0,
                    "DCM_Capacity_kW": 100.0, "DCM_Airflow_m3h": 20000.0,
                    "DCM_CHW_DN": 100, "DCM_FrontFaces": "SOUTH"}})

# PDUs -----------------------------------------------------------------------
PDU_DATA = []
PDU_ROW_Y0 = {"PDU-01": 2400.0, "PDU-02": 5400.0, "PDU-03": 7800.0,
              "PDU-04": 10800.0, "PDU-05": 13200.0, "PDU-06": 16200.0}
for tag, addr, facing in PDUS:
    tx, ty = tile_to_xy(addr)
    # A-101 note 8: the PDU front is flush with the front face of the row it
    # serves.  South-facing PDUs already have their front on the row south face;
    # north-facing PDUs are moved north by 387 mm from the tile SW corner.
    row_y0 = PDU_ROW_Y0[tag]
    if facing == "NORTH":
        y0 = row_y0 + ROW_DEPTH - PDU_D
    else:
        y0 = row_y0
    x0 = tx
    theta = 0.0 if facing == "SOUTH" else 180.0
    cx, cy = x0 + PDU_W/2.0, y0 + PDU_D/2.0
    add_box("IfcElectricDistributionBoard", tag, "PDU", "DISTRIBUTIONBOARD",
            cx, cy, 0.0, PDU_W, PDU_D, PDU_HEIGHT, theta, tag, "pdu:"+tag,
            common_extra={"DCM_Category": "PDU", "DCM_Tag": tag},
            loc_extra={"DCM_Row": chr(ord("A") + int(tag[-2:]) - 1), "DCM_Tile": addr, "DCM_Facing": facing},
            specific={"Pset_DCM_Equipment": {
                "DCM_EquipmentType": "Power Distribution Unit", "Width_mm": PDU_W,
                "Depth_mm": PDU_D, "Height_mm": PDU_HEIGHT, "Rating_kVA": 225.0,
                "FrontFaces": facing, "DedicatedSpace_mm": PDU_DEDICATED,
                "WorkingSpace_mm": 900.0},
                "Pset_DCM_PDU": {
                    "DCM_Tag": tag, "DCM_Row": chr(ord("A") + int(tag[-2:]) - 1),
                    "DCM_Tile": addr, "DCM_Width_mm": PDU_W, "DCM_Depth_mm": PDU_D,
                    "DCM_Height_mm": PDU_HEIGHT, "DCM_Rating_kVA": 225.0,
                    "DCM_FrontFaces": facing, "DCM_DedicatedSpace_mm": PDU_DEDICATED,
                    "DCM_WorkingSpace_mm": 900.0}})
    PDU_DATA.append((tag, x0, y0, x0 + PDU_W, y0 + PDU_D, PDU_HEIGHT))

# Columns --------------------------------------------------------------------
for i, (x0, y0) in enumerate(COLUMNS):
    cx, cy = x0 + COL_W/2.0, y0 + COL_W/2.0
    tag = "COL-%02d" % (i+1)
    add_box("IfcColumn", tag, "Structural Column", "COLUMN",
            cx, cy, 0.0, COL_W, COL_W, COL_H, 0.0, tag, "col:"+tag,
            common_extra={"DCM_Category": "Structure", "DCM_Tag": tag},
            loc_extra={"DCM_Tile": tile_address(x0, y0)},
            specific={"Pset_DCM_Column": {
                "DCM_Height_mm": COL_H, "DCM_Base_mm": 0.0, "DCM_Top_mm": COL_H,
                "DCM_Size_mm": COL_W}})

# Access floor ----------------------------------------------------------------
add_box("IfcSlab", "Access Floor", "Access Floor", "FLOOR",
        ROOM_X/2.0, ROOM_Y/2.0, -PANEL_T, ROOM_X, ROOM_Y, PANEL_T, 0.0,
        "FLOOR-01", "floor:01",
        common_extra={"DCM_Category": "Access Floor", "DCM_Tag": "FLOOR-01"},
        loc_extra={"DCM_Tile": "A01"},
        specific={"Pset_DCM_Floor": {
            "DCM_PanelThickness_mm": PANEL_T, "DCM_TopElevation_mm": 0.0,
            "DCM_PlenumDepth_mm": PLENUM_VOID, "DCM_AccessFloorHeight_mm": ACCESS_FLOOR_HEIGHT,
            "DCM_StructuralSlabTop_mm": STRUCT_SLAB_TOP,
            "DCM_TilePitch_mm": TILE}})

# Containment -----------------------------------------------------------------
cont_count = 0
for (x0, x1, yc) in CONTAINMENT:
    cont_count += 1
    tag = "CAC-PANEL-%02d" % cont_count
    cx, cy = (x0+x1)/2.0, yc
    add_box("IfcCovering", tag, "Containment Roof", "CEILING",
            cx, cy, CONT_ROOF_Z, x1-x0, CONT_ROOF_W, CONT_ROOF_T, 0.0,
            tag, "cont:"+tag,
            common_extra={"DCM_Category": "Containment", "DCM_Tag": tag},
            loc_extra={"DCM_Tile": tile_address(x0, yc-CONT_ROOF_W/2.0)},
            specific={"Pset_DCM_Containment": {
                "DCM_RoofWidth_mm": CONT_ROOF_W, "DCM_RoofThickness_mm": CONT_ROOF_T,
                "DCM_RoofUnderside_mm": CONT_ROOF_Z, "DCM_Aisle": "B/C" if yc < 10000 else "D/E"}})
door_count = 0
for (x0, x1, yc) in CONTAINMENT:
    for xd in (x0 - CONT_DOOR_T, x1):
        door_count += 1
        tag = "CAC-DOOR-%02d" % door_count
        add_box("IfcBuildingElementProxy", tag, "Containment Door", "ELEMENT",
                xd + CONT_DOOR_T/2.0, yc, 0.0, CONT_DOOR_T, 1200.0, CONT_DOOR_H, 0.0,
                tag, "door:"+tag,
                common_extra={"DCM_Category": "Containment", "DCM_Tag": tag},
                loc_extra={"DCM_Tile": tile_address(xd, yc-600.0)},
                specific={"Pset_DCM_Containment": {
                    "DCM_DoorThickness_mm": CONT_DOOR_T, "DCM_DoorHeight_mm": CONT_DOOR_H}})

# Sprinkler heads -------------------------------------------------------------
HEAD_DATA = []
for i, (x, y) in enumerate(CEIL_HEADS):
    tag = "SPK-C-%02d" % (i+1)
    add_cyl("IfcFireSuppressionTerminal", tag, "Sprinkler", "SPRINKLER",
            x, y, DEFLECTOR, 40.0, SOFFIT - DEFLECTOR, tag, "spk:"+tag,
            common_extra={"DCM_Category": "Fire Protection", "DCM_Tag": tag},
            loc_extra={"DCM_Tile": tile_address(x, y)},
            specific={"Pset_DCM_Sprinkler": {
                "DCM_HeadType": "Ceiling Pendent", "DCM_DeflectorElevation_mm": DEFLECTOR,
                "DCM_SpacingX_mm": 3000.0, "DCM_SpacingY_mm": 3000.0,
                "DCM_Coverage_m2": 9.0}})
    HEAD_DATA.append((tag, x, y, DEFLECTOR, "Ceiling"))
for i, (x, y) in enumerate(IN_AISLE_HEADS):
    tag = "SPK-A-%02d" % (i+1)
    add_cyl("IfcFireSuppressionTerminal", tag, "Sprinkler", "SPRINKLER",
            x, y, IN_AISLE_DEFLECTOR, 40.0, CONT_ROOF_Z - IN_AISLE_DEFLECTOR, tag, "spka:"+tag,
            common_extra={"DCM_Category": "Fire Protection", "DCM_Tag": tag},
            loc_extra={"DCM_Tile": tile_address(x, y)},
            specific={"Pset_DCM_Sprinkler": {
                "DCM_HeadType": "In-aisle under containment roof",
                "DCM_DeflectorElevation_mm": IN_AISLE_DEFLECTOR,
                "DCM_BelowRoof_mm": CONT_ROOF_Z - IN_AISLE_DEFLECTOR}})
    HEAD_DATA.append((tag, x, y, IN_AISLE_DEFLECTOR, "In-aisle"))

# ----------------------------------------------------------------------------
# Services
# ----------------------------------------------------------------------------
runs = {"TRAY": [], "CHW": [], "BUS": []}
RUN_GEOM = {"TRAY": [], "CHW": [], "BUS": []}

def add_run(service, name, p0, p1, profile, key_prefix, objtype=None, as_proxy=False):
    """profile: ('rect', width, height) or ('circ', diameter); p0/p1 are solid
    centreline end points (the solid spans from p0 to p1)."""
    pl, L = placement_run(p0, p1)
    if profile[0] == "rect":
        rep = body_rep(rect_profile(profile[1], profile[2]), L)
    else:
        rep = body_rep(circ_profile(profile[1]/2.0), L)
    if as_proxy:
        # A distinct drop/termination element.  It is a pipe fitting so that the
        # network/clash tools see it as part of the same CHW run at its butt joint.
        el = f.createIfcPipeFitting(gid(key_prefix+name), None, name, None,
                                    objtype or "Drop / Termination", pl, rep, name, None)
    elif service == "TRAY":
        el = f.createIfcCableCarrierSegment(gid(key_prefix+name), None, name, None,
                                            "Telecom Cable Tray", pl, rep, name, "CABLELADDERSEGMENT")
    elif service == "BUS":
        el = f.createIfcCableCarrierSegment(gid(key_prefix+name), None, name, None,
                                            "Power Busway", pl, rep, name, "CABLETRUNKINGSEGMENT")
    elif service == "CHW":
        el = f.createIfcPipeSegment(gid(key_prefix+name), None, name, None,
                                    objtype or "Chilled Water Pipe", pl, rep, name, "RIGIDSEGMENT")
    else:
        raise ValueError(service)
    # per-segment properties
    zone = "Underfloor" if p0[2] < 0 else "Overhead"
    vertical = (abs(p1[2]-p0[2]) > 1e-6 and
                abs(p1[0]-p0[0]) < 1e-6 and abs(p1[1]-p0[1]) < 1e-6)
    if abs(p1[0]-p0[0]) > abs(p1[1]-p0[1]):
        orient = "East-West"
    elif abs(p1[1]-p0[1]) > 1e-6:
        orient = "North-South"
    else:
        orient = "Vertical"
    if profile[0] == "rect":
        sw, sh = profile[1], profile[2]
        zc = (p0[2] + p1[2]) / 2.0 if vertical else p0[2]
        zlo, zhi = ((min(p0[2], p1[2]), max(p0[2], p1[2])) if vertical
                    else (zc - sh/2.0, zc + sh/2.0))
        extra = {"DCM_SectionWidth_mm": sw, "DCM_SectionHeight_mm": sh}
    else:
        sw = sh = profile[1]
        zc = (p0[2] + p1[2]) / 2.0 if vertical else p0[2]
        zlo, zhi = ((min(p0[2], p1[2]), max(p0[2], p1[2])) if vertical
                    else (zc - profile[1]/2.0, zc + profile[1]/2.0))
        bare_od = PIPE_BARE_OD if abs(profile[1] - PIPE_OD) < 1.0 else (profile[1] - 2.0 * INSUL_THK)
        extra = {"DCM_OutsideDiameter_mm": profile[1],
                 "DCM_BareOD_mm": bare_od, "DCM_InsulationThickness_mm": INSUL_THK}
    common = dict(COMMON_MODEL)
    common.update({"DCM_Category": "Pathway" if service != "CHW" else "Piping",
                   "DCM_Tag": name, "DCM_Service": service})
    loc = {"DCM_StartX_mm": float(p0[0]), "DCM_StartY_mm": float(p0[1]),
           "DCM_StartZ_mm": float(p0[2]), "DCM_EndX_mm": float(p1[0]),
           "DCM_EndY_mm": float(p1[1]), "DCM_EndZ_mm": float(p1[2]),
           "DCM_Length_mm": float(L), "DCM_Zone": zone, "DCM_Orientation": orient,
           "DCM_CenterlineElevation_mm": float(zc)}
    if service == "BUS":
        extra["DCM_MaxSupportSpacing_mm"] = 1500.0
    spec = {"Pset_DCM_Pathway": dict({"DCM_Service": service, "DCM_Length_mm": float(L),
                                      "DCM_Zone": zone, "DCM_Orientation": orient,
                                      "DCM_ZBottom_mm": float(zlo), "DCM_ZTop_mm": float(zhi)},
                                     **extra),
            "Pset_DCM_Clearance": dict(
                {"DCM_MinHeadroom_mm": MIN_HEADROOM,
                 "DCM_SprinklerStandoff_mm": CLEAR_BELOW_DEFLECTOR,
                 "DCM_TrayBuswaySeparation_mm": TRAY_BUS_SEP,
                 "DCM_PDUDedicatedSpace_mm": PDU_DEDICATED,
                 "DCM_TrayBuswayAchievedSeparation_mm": TRAY_Z0 - (BUS_Z0 + BUS_H)},
                **({"DCM_AchievedHeadroom_mm": zlo,
                    "DCM_AchievedClearBelowDeflector_mm": DEFLECTOR - zhi} if p0[2] > 0 else
                   {"DCM_DepthBelowFinishedFloor_mm": -zhi}))}
    add_pset(el, "Pset_DCM_Common", common, key_prefix+name)
    add_pset(el, "Pset_DCM_Location", loc, key_prefix+name)
    for pn, pp in spec.items():
        add_pset(el, pn, pp, key_prefix+name)
    elements.append(el)
    runs[service].append(el)
    half = profile[1] / 2.0
    if vertical:
        zlo, zhi = min(p0[2], p1[2]), max(p0[2], p1[2])
    else:
        zlo = (p0[2] - profile[2] / 2.0) if profile[0] == "rect" else (p0[2] - profile[1] / 2.0)
        zhi = (p0[2] + profile[2] / 2.0) if profile[0] == "rect" else (p0[2] + profile[1] / 2.0)
    lo = [min(p0[0], p1[0]), min(p0[1], p1[1]), zlo]
    hi = [max(p0[0], p1[0]), max(p0[1], p1[1]), zhi]
    if abs(p1[0]-p0[0]) > 1e-6:
        lo[1] = p0[1] - half; hi[1] = p0[1] + half
    elif abs(p1[1]-p0[1]) > 1e-6:
        lo[0] = p0[0] - half; hi[0] = p0[0] + half
    if not as_proxy:
        RUN_GEOM[service].append((name, tuple(lo), tuple(hi), zlo, zhi))
    return el

# Tray (overhead, 2880..3007), width 683, height 127
tz = TRAY_ZC
CONNECTIONS = []
def connect(parent, child):
    CONNECTIONS.append((parent, child))
tray_entry = add_run("TRAY", "CT-1 entry", (0.0, 9600.0, tz),
                     (TRAY_TRUNK_X - TRAY_W/2.0, 9600.0, tz), ("rect", TRAY_W, TRAY_H), "tray:")
tray_trunk = add_run("TRAY", "CT-1 trunk", (TRAY_TRUNK_X, TRAY_LANES["AB"], tz),
                     (TRAY_TRUNK_X, TRAY_LANES["EF"], tz), ("rect", TRAY_W, TRAY_H), "tray:")
connect(tray_entry, tray_trunk)
for lane in ("AB", "CD", "EF"):
    br = add_run("TRAY", "CT-1 %s main" % lane,
                 (TRAY_TRUNK_X + TRAY_W/2.0, TRAY_LANES[lane], tz),
                 (MAIN_X1, TRAY_LANES[lane], tz), ("rect", TRAY_W, TRAY_H), "tray:")
    connect(tray_trunk, br)

# CHW (overhead): one DN100 west trunk, a full DN50 header along every cabinet
# row (M-101 note 3), a DN100 perimeter gallery header, and a drop to every CRAH.
cz = CHW_ZC
chw_entry = add_run("CHW", "CHW-1 entry", (0.0, 9600.0, cz),
                    (CHW_TRUNK_X - PIPE_OD/2.0, 9600.0, cz), ("circ", PIPE_OD), "chw:")
chw_trunk = add_run("CHW", "CHW-1 west trunk", (CHW_TRUNK_X, 450.0, cz),
                    (CHW_TRUNK_X, 17700.0, cz), ("circ", PIPE_OD), "chw:")
connect(chw_entry, chw_trunk)

# A-101 note 2: west service strip carries the trunks and risers.  For rows C
# and F the header is set 900 mm north of the row centreline so that it passes
# clear of the 600 mm columns on grid y=8400/16800; the 900 mm CRAH branch
# keeps every in-row unit connected.
ROW_CENTRE = {"A": 3000.0, "B": 6000.0, "C": 8400.0,
              "D": 11400.0, "E": 13800.0, "F": 16800.0}
HEADER_Y = {"A": 3000.0, "B": 6000.0, "C": 9300.0,
            "D": 11400.0, "E": 13800.0, "F": 17700.0}
CRAH_TOP = 2000.0
DN50_BOTTOM = CHW_ZC - PIPE_BRANCH_OD / 2.0
for rname, y0, facing, seq in ROWS:
    row_end = ROW_X0 + row_bays[rname][1]
    hy = HEADER_Y[rname]
    hdr = add_run("CHW", "CHW-1 row %s header" % rname,
                  (CHW_TRUNK_X + PIPE_OD/2.0, hy, cz), (row_end, hy, cz),
                  ("circ", PIPE_BRANCH_OD), "chw:")
    connect(chw_trunk, hdr)
    for tag, bx, bw, kind in row_bays[rname][0]:
        if kind != "CRAH":
            continue
        xc = bx + bw/2.0
        yc = ROW_CENTRE[rname]
        if abs(hy - yc) < 1e-6:
            drop_from = hdr
        else:
            br = add_run("CHW", "CHW-1 %s branch to %s" % (rname, tag),
                         (xc, hy - PIPE_BRANCH_OD/2.0, cz), (xc, yc, cz),
                         ("circ", PIPE_BRANCH_OD), "chw:")
            connect(hdr, br)
            drop_from = br
        drop = add_run("CHW", "CHW-1 drop to %s" % tag,
                       (xc, yc, CRAH_TOP), (xc, yc, DN50_BOTTOM),
                       ("circ", PIPE_BRANCH_OD), "chw:",
                       objtype="CHW DN50 Drop / Termination", as_proxy=True)
        connect(drop_from, drop)

# DN100 perimeter gallery header along y=450, directly over the four perimeter
# CRAH centres, with a DN100 drop to each unit.
perim_hdr = add_run("CHW", "CHW-1 perimeter header",
                    (CHW_TRUNK_X + PIPE_OD/2.0, 450.0, cz), (25800.0, 450.0, cz),
                    ("circ", PIPE_OD), "chw:")
connect(chw_trunk, perim_hdr)
for tag, px0, py0 in PERIM_CRAH:
    xc = px0 + 600.0
    drop = add_run("CHW", "CHW-1 drop to %s" % tag,
                   (xc, 450.0, CRAH_TOP), (xc, 450.0, CHW_ZC - PIPE_OD/2.0),
                   ("circ", PIPE_OD), "chw:",
                   objtype="CHW DN100 Drop / Termination", as_proxy=True)
    connect(perim_hdr, drop)

# Busway (underfloor plenum, -300..-153), 128 x 147.  Each aisle main is extended
# east to the PDU column, then a branch and a riser reach every PDU (E-101 one-line).
bz = BUS_ZC
bus_entry = add_run("BUS", "BW-1 entry", (0.0, 9600.0, bz),
                    (BUS_TRUNK_X - BUS_W/2.0, 9600.0, bz), ("rect", BUS_W, BUS_H), "bus:")
bus_trunk = add_run("BUS", "BW-1 trunk", (BUS_TRUNK_X, BUS_LANES["AB"], bz),
                    (BUS_TRUNK_X, BUS_LANES["EF"], bz), ("rect", BUS_W, BUS_H), "bus:")
connect(bus_entry, bus_trunk)
bus_mains = {}
for lane in ("AB", "CD", "EF"):
    br = add_run("BUS", "BW-1 %s main" % lane,
                 (BUS_TRUNK_X + BUS_W/2.0, BUS_LANES[lane], bz),
                 (BUS_PDU_X1, BUS_LANES[lane], bz), ("rect", BUS_W, BUS_H), "bus:")
    bus_mains[lane] = br
    connect(bus_trunk, br)

BUS_PDU = [
    ("PDU-01", "AB", 21381.0, 2806.5, True),
    ("PDU-02", "AB", 21981.0, 6193.5, False),
    ("PDU-03", "CD", 21381.0, 8206.5, True),
    ("PDU-04", "CD", 21981.0, 11593.5, False),
    ("PDU-05", "EF", 21381.0, 13606.5, True),
    ("PDU-06", "EF", 21981.0, 16993.5, False),
]
for tag, lane, xc, yc, south in BUS_PDU:
    yface = BUS_LANES[lane] - BUS_W/2.0 if south else BUS_LANES[lane] + BUS_W/2.0
    br = add_run("BUS", "BW-1 branch to %s" % tag, (xc, yface, bz), (xc, yc, bz),
                 ("rect", BUS_W, BUS_H), "bus:")
    connect(bus_mains[lane], br)
    riser = add_run("BUS", "BW-1 riser to %s" % tag,
                    (xc, yc, BUS_Z0 + BUS_H), (xc, yc, -PANEL_T),
                    ("rect", BUS_W, BUS_H), "bus:",
                    objtype="Power Busway - Drop / Termination to PDU")
    connect(br, riser)

# Explicit connection relationships between parent and child route elements.
for parent, child in CONNECTIONS:
    f.createIfcRelConnectsElements(gid("connect:"+parent.Name+":"+child.Name), None, None, None,
                                   None, parent, child)

# Service groups --------------------------------------------------------------
groups = {}
for service, name, desc in (("TRAY", "CT-1 -- Telecom Cable Tray", "ANSI/TIA-942 telecom ladder tray 683x127"),
                            ("BUS", "BW-1 -- Power Busway", "Busway 128x147, under-floor plenum"),
                            ("CHW", "CHW-1 -- Chilled Water", "DN100 CHW, 25.4 mm insulation, 168.3 mm envelope")):
    g = f.createIfcGroup(gid("group:"+service), None, name, desc, service)
    f.createIfcRelAssignsToGroup(gid("grouprel:"+service), None, None, None, runs[service], None, g)
    groups[service] = g

# Diagnostic clearance properties ------------------------------------------------
by_name = {}
for _e in elements:
    if _e.Name:
        by_name.setdefault(_e.Name, []).append(_e)

def plan_rect_dist(px, py, lo, hi):
    dx = max(0.0, lo[0]-px, px-hi[0])
    dy = max(0.0, lo[1]-py, py-hi[1])
    return math.hypot(dx, dy)

def box3_dist(a_lo, a_hi, b_lo, b_hi):
    d = [max(0.0, a_lo[0]-b_hi[0], b_lo[0]-a_hi[0]),
         max(0.0, a_lo[1]-b_hi[1], b_lo[1]-a_hi[1]),
         max(0.0, a_lo[2]-b_hi[2], b_lo[2]-a_hi[2])]
    return math.sqrt(sum(x*x for x in d))

for tag, x, y, defl, kind in HEAD_DATA:
    best_plan = None
    for s in ("TRAY", "CHW", "BUS"):
        for name, lo, hi, zlo, zhi in RUN_GEOM[s]:
            pd = plan_rect_dist(x, y, lo, hi)
            if pd <= 450.0 and zhi <= defl:
                clear = defl - zhi
                if best_plan is None or clear < best_plan[0]:
                    best_plan = (clear, name, pd)
    el = by_name[tag][0]
    props = {"DCM_HeadType": kind, "DCM_DeflectorElevation_mm": defl,
             "DCM_SprinklerStandoff_mm": CLEAR_BELOW_DEFLECTOR}
    if best_plan is not None:
        props.update({"DCM_ServiceBelow": best_plan[1],
                      "DCM_VerticalClearance_mm": best_plan[0],
                      "DCM_PlanDistance_mm": best_plan[2]})
    add_pset(el, "Pset_DCM_Clearance", props, "headclear:"+tag)

for tag, x0, y0, x1, y1, top in PDU_DATA:
    best = None
    for name, lo, hi, zlo, zhi in RUN_GEOM["CHW"]:
        d = box3_dist((x0, y0, top), (x1, y1, top), (lo[0], lo[1], lo[2]), (hi[0], hi[1], hi[2]))
        if best is None or d < best[0]:
            best = (d, name, zlo)
    el = by_name[tag][0]
    props = {"DCM_PDUTop_mm": top, "DCM_DedicatedSpace_mm": PDU_DEDICATED,
             "DCM_WorkingSpace_mm": 900.0,
             "DCM_NearestCHW_Distance_mm": best[0], "DCM_NearestCHW": best[1]}
    if best[2] >= top:
        props["DCM_VerticalClearanceToCHW_mm"] = best[2] - top
    add_pset(el, "Pset_DCM_Clearance", props, "pduclear:"+tag)

for service, g in groups.items():
    total = sum(max(hi[i]-lo[i] for i in range(3)) for name, lo, hi, zlo, zhi in RUN_GEOM[service])
    zone = "Underfloor" if service == "BUS" else "Overhead"
    svc_extra = {}
    if service == "CHW":
        svc_extra = {"DCM_RowHeaders": 6, "DCM_Drops": 22,
                     "DCM_DropLength_mm": 18.0 * (DN50_BOTTOM - CRAH_TOP) + 4.0 * (CHW_ZC - PIPE_OD/2.0 - CRAH_TOP)}
    elif service == "BUS":
        svc_extra = {"DCM_PDUBranches": 6, "DCM_PDURisers": 6}
    add_pset(g, "Pset_DCM_Service", {
        "DCM_Service": service,
        "DCM_Zone": zone,
        "DCM_TotalLength_mm": total,
        "DCM_EntryX_mm": 0.0, "DCM_EntryY_mm": 9600.0,
        "DCM_RowsServed": "A,B,C,D,E,F",
        "DCM_TrayBuswaySeparation_mm": TRAY_BUS_SEP,
        "DCM_MinHeadroom_mm": MIN_HEADROOM,
        "DCM_SprinklerStandoff_mm": CLEAR_BELOW_DEFLECTOR,
        **svc_extra,
    }, "groupsvc:"+service)

# Project / level summary properties -------------------------------------------
_total_route = sum(max(hi[i]-lo[i] for i in range(3))
                   for svc in RUN_GEOM for name, lo, hi, zlo, zhi in RUN_GEOM[svc])
add_pset(project, "Pset_DCM_Project", {
    "DCM_Project": "dc_model hall_seed000_d000",
    "DCM_ProjectNo": "MDC-2026-014",
    "DCM_Status": "ISSUED FOR CONSTRUCTION",
    "DCM_Units": "millimetre",
    "DCM_RoomWidth_mm": ROOM_X,
    "DCM_RoomDepth_mm": ROOM_Y,
    "DCM_TilePitch_mm": TILE,
    "DCM_RackCount": 128,
    "DCM_CRAHCount": 22,
    "DCM_PDUCount": 6,
    "DCM_ServiceCount": 3,
    "DCM_TotalRouteLength_mm": _total_route,
    "DCM_ModelSource": "A-101/A-301/A-601/A-602/E-101/F-101/M-101, issued for construction 2026-07-24/27",
}, "project:summary")
add_pset(storey, "Pset_DCM_Level", {
    "DCM_LevelName": "Level 0 - Data Hall",
    "DCM_Elevation_mm": 0.0,
    "DCM_Soffit_mm": SOFFIT,
    "DCM_StructuralSlabTop_mm": STRUCT_SLAB_TOP,
    "DCM_MinClearHeight_mm": MIN_HEADROOM,
    "DCM_SprinklerDeflector_mm": DEFLECTOR,
    "DCM_ClearBelowDeflector_mm": CLEAR_BELOW_DEFLECTOR,
    "DCM_OverheadBand_mm": "2600-3114.6",
    "DCM_UnderfloorPlenum_mm": PLENUM_VOID,
}, "storey:summary")

# Space -----------------------------------------------------------------------
# IfcSpace is a spatial structure element: aggregate it to the storey (WR41),
# do not put it in the IfcRelContainedInSpatialStructure set.
sp_pl = placement_xyz(ROOM_X/2.0, ROOM_Y/2.0, 0.0, 0.0)
# the space is a spatial volume only (no body solid), so it can never be
# mistaken for an obstruction by a clash checker that does not skip IfcSpace
sp = f.createIfcSpace(gid("space:real"), None, "DATA HALL", None, "Space", sp_pl, None,
                      None, "ELEMENT", "SPACE", None)
f.createIfcRelAggregates(gid("spaceagg"), None, None, None, storey, [sp])
add_pset(sp, "Pset_DCM_Common", dict(COMMON_MODEL, DCM_Category="Space", DCM_Tag="DATA HALL"), "space:real")
add_pset(sp, "Pset_DCM_Location", {"DCM_X_mm": ROOM_X/2.0, "DCM_Y_mm": ROOM_Y/2.0, "DCM_Z_mm": 0.0}, "space:real")
add_pset(sp, "Pset_DCM_Space", {
    "DCM_SpaceName": "DATA HALL", "DCM_Width_mm": ROOM_X, "DCM_Depth_mm": ROOM_Y,
    "DCM_ClearHeight_mm": SOFFIT, "DCM_FinishedFloor_mm": 0.0,
    "DCM_Soffit_mm": SOFFIT, "DCM_Use": "Data Hall",
    "DCM_Occupancy": "Equipment space (unoccupied for people except maintenance)",
    "DCM_TilePitch_mm": TILE}, "space:real")

# Containment in the storey ---------------------------------------------------
f.createIfcRelContainedInSpatialStructure(gid("contain"), None, None, None, elements, storey)

# ----------------------------------------------------------------------------
# Validate and write
# ----------------------------------------------------------------------------
class _Collect(logging.Handler):
    def __init__(self):
        super().__init__()
        self.msgs = []
    def emit(self, record):
        self.msgs.append(record.getMessage())

logger = logging.getLogger("dcm_validate")
logger.propagate = False
logger.setLevel(logging.DEBUG)
handler = _Collect()
logger.addHandler(handler)
ifcopenshell.validate.validate(f, logger, express_rules=True)
if handler.msgs:
    sys.stderr.write("IFC validation issues:\n")
    for m in handler.msgs[:20]:
        sys.stderr.write("  " + m.replace("\n", " | ")[:500] + "\n")
    raise SystemExit("model failed express_rules validation")

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.ifc")
f.header.file_name.time_stamp = "2026-07-27T00:00:00"
f.header.file_name.name = os.path.basename(out)
f.write(out)
print("wrote", out, "elements:", len(elements), "racks:", rack_count, "crahs:", crah_count + 4,
      "tray runs:", len(runs["TRAY"]), "bus runs:", len(runs["BUS"]), "chw runs:", len(runs["CHW"]))
