#!/usr/bin/env python3
"""AHPELE deliverable checker (runs inside the task container).

Re-opens each deliverable the way a grader's parser would and reports problems:
missing or empty files, unreadable archives, CSV/JSON/XLSX/DOCX/IFC that do not
parse, placeholder values (TBD, NaN, ...), Python that does not compile.
Standard library only; uses ifcopenshell when it is importable.

Generic by design: it knows file formats, never anything about a task. It does
not judge engineering correctness; that is what your own requirement checks are for.

Usage: python3 ahpele_check.py <file-or-dir> [<file-or-dir> ...] [--expect-columns a,b,c]
Exit code 0 when no problem was found, 1 otherwise.
"""
from __future__ import annotations

import csv
import io
import json
import os
import py_compile
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

PLACEHOLDER = re.compile(r"^\s*(TBD|TBA|TBC|to be (determined|advised|confirmed)|NaN|-?Inf(inity)?|XXX+|<fill[^>]*>|"
                         r"\?\?+|TODO|FIXME|placeholder|lorem ipsum)\s*$", re.I)
PLACEHOLDER_IN_TEXT = re.compile(r"\b(TBD|TBA|TODO|FIXME|XXX+|lorem ipsum)\b|<fill in>|\[insert[^\]]*\]", re.I)
problems: list[str] = []
notes: list[str] = []


def problem(msg):
    problems.append(msg)


def note(msg):
    notes.append(msg)


def check_csv(name, data):
    text = data.decode("utf-8-sig", "replace")
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error as exc:
        problem(f"{name}: CSV does not parse: {exc}")
        return
    if not rows:
        problem(f"{name}: CSV is empty")
        return
    header = [h.strip() for h in rows[0]]
    if len(set(h.lower() for h in header)) != len(header):
        problem(f"{name}: duplicate column names in header {header}")
    if any(not h for h in header):
        problem(f"{name}: empty column name in header")
    widths = {len(r) for r in rows[1:] if r}
    if widths and widths != {len(header)}:
        problem(f"{name}: rows have {sorted(widths)} cells but the header has {len(header)}")
    bad = [(i + 2, header[j] if j < len(header) else j, c) for i, r in enumerate(rows[1:]) for j, c in enumerate(r)
           if PLACEHOLDER.match(c or "")]
    if bad:
        problem(f"{name}: {len(bad)} placeholder cell(s), e.g. row {bad[0][0]} column {bad[0][1]!r} = {bad[0][2]!r}")
    note(f"{name}: CSV {len(rows) - 1} rows x {len(header)} columns: {', '.join(header[:30])}"
         f"{' ...' if len(header) > 30 else ''}")
    expect = os.environ.get("AHPELE_EXPECT_COLUMNS")
    if expect:
        norm = lambda s: re.sub(r"[\s_\-]+", "_", s.strip().lower())  # noqa: E731
        missing = [c for c in expect.split(",") if norm(c) not in {norm(h) for h in header}]
        if missing:
            problem(f"{name}: missing expected columns {missing}")


def check_json(name, data):
    try:
        obj = json.loads(data.decode("utf-8-sig"))
    except ValueError as exc:
        problem(f"{name}: JSON does not parse: {exc}")
        return
    def walk(o, path="$"):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o[:2000]):
                yield from walk(v, f"{path}[{i}]")
        elif isinstance(o, str) and PLACEHOLDER.match(o):
            yield path, o
        elif isinstance(o, float) and (o != o or o in (float("inf"), float("-inf"))):
            yield path, o
    bad = list(walk(obj))
    if bad:
        problem(f"{name}: {len(bad)} placeholder/NaN value(s), e.g. {bad[0][0]} = {bad[0][1]!r}")
    keys = list(obj.keys())[:30] if isinstance(obj, dict) else f"list[{len(obj)}]" if isinstance(obj, list) else type(obj).__name__
    note(f"{name}: JSON top level: {keys}")


def xml_text(z, member):
    return "".join(t for t in ET.fromstring(z.read(member)).itertext())


def check_docx(name, data):
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        text = xml_text(z, "word/document.xml")
    except Exception as exc:  # noqa: BLE001
        problem(f"{name}: DOCX does not open: {type(exc).__name__}: {exc}")
        return
    words = len(text.split())
    if words < 30:
        problem(f"{name}: DOCX has only {words} words")
    m = PLACEHOLDER_IN_TEXT.search(text)
    if m:
        problem(f"{name}: DOCX contains placeholder text {m.group(0)!r}")
    note(f"{name}: DOCX {words} words")


def check_xlsx(name, data):
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
    except Exception as exc:  # noqa: BLE001
        problem(f"{name}: XLSX does not open: {type(exc).__name__}: {exc}")
        return
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    sheets = [s.get("name") for s in wb.findall("s:sheets/s:sheet", ns)]
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        shared = ["".join(t.itertext()) for t in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si", ns)]
    bad = [s for s in shared if PLACEHOLDER.match(s)]
    errors = 0
    for member in z.namelist():
        if member.startswith("xl/worksheets/") and member.endswith(".xml"):
            errors += len(re.findall(rb'<c [^>]*t="e"', z.read(member)))
    if bad:
        problem(f"{name}: XLSX has placeholder text {bad[:3]}")
    if errors:
        problem(f"{name}: XLSX has {errors} cell(s) holding formula errors (#REF!, #DIV/0!, ...)")
    note(f"{name}: XLSX sheets {sheets}")


def check_ifc(name, data, path=None):
    head = data[:2000].decode("utf-8", "replace")
    if "ISO-10303-21" not in head:
        problem(f"{name}: IFC does not start with ISO-10303-21 (not a STEP file)")
        return
    m = re.search(r"FILE_SCHEMA\s*\(\s*\(\s*'([^']+)'", head)
    note(f"{name}: IFC schema {m.group(1) if m else '?'}")
    try:
        import ifcopenshell  # noqa: F401
    except ImportError:
        note(f"{name}: ifcopenshell not importable here; only the header was checked")
        return
    try:
        import tempfile
        import ifcopenshell
        if path is None:
            with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False) as fh:
                fh.write(data)
                path = fh.name
        f = ifcopenshell.open(path)
        counts = {t: len(f.by_type(t)) for t in ("IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey",
                                                  "IfcSpace", "IfcPropertySet", "IfcProduct")}
        note(f"{name}: IFC opens with ifcopenshell: {counts}")
        if counts["IfcProject"] != 1:
            problem(f"{name}: IFC has {counts['IfcProject']} IfcProject entities (expected exactly 1)")
    except Exception as exc:  # noqa: BLE001
        problem(f"{name}: IFC does not open with ifcopenshell: {type(exc).__name__}: {exc}")


def check_text(name, data):
    text = data.decode("utf-8", "replace")
    m = PLACEHOLDER_IN_TEXT.search(text)
    if m:
        problem(f"{name}: placeholder text {m.group(0)!r}")
    note(f"{name}: {len(text.split())} words")


def check_member(name, data, path=None):
    if not data:
        problem(f"{name}: empty file")
        return
    ext = os.path.splitext(name)[1].lower()
    if ext == ".csv":
        check_csv(name, data)
    elif ext == ".json":
        check_json(name, data)
    elif ext == ".docx":
        check_docx(name, data)
    elif ext in (".xlsx", ".xlsm"):
        check_xlsx(name, data)
    elif ext == ".ifc":
        check_ifc(name, data, path)
    elif ext in (".md", ".txt"):
        check_text(name, data)
    elif ext == ".py":
        if path:
            try:
                py_compile.compile(path, doraise=True)
                note(f"{name}: Python compiles")
            except py_compile.PyCompileError as exc:
                problem(f"{name}: Python does not compile: {exc.msg[:200]}")
    elif ext == ".zip":
        check_zip(name, data)
    else:
        note(f"{name}: {len(data)} bytes (format not checked)")


def check_zip(name, data):
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        bad = z.testzip()
    except zipfile.BadZipFile as exc:
        problem(f"{name}: not a valid zip: {exc}")
        return
    if bad:
        problem(f"{name}: corrupt member {bad}")
    members = [i for i in z.infolist() if not i.is_dir()]
    nested = [i.filename for i in members if "/" in i.filename.strip("/")]
    note(f"{name}: zip with {len(members)} file(s): {', '.join(i.filename for i in members[:40])}")
    if nested:
        note(f"{name}: members inside folders (check the instruction wants that): {nested[:5]}")
    for i in members:
        check_member(f"{name}!{i.filename}", z.read(i))


def main(argv):
    targets = [a for a in argv if not a.startswith("--")]
    if "--expect-columns" in argv:
        os.environ["AHPELE_EXPECT_COLUMNS"] = argv[argv.index("--expect-columns") + 1]
        targets = [t for t in targets if t != os.environ["AHPELE_EXPECT_COLUMNS"]]
    if not targets:
        print(__doc__)
        return 2
    for t in targets:
        if not os.path.exists(t):
            problem(f"{t}: does not exist")
            continue
        paths = [t] if os.path.isfile(t) else [os.path.join(dp, f) for dp, _, fs in os.walk(t) for f in sorted(fs)]
        if not paths:
            problem(f"{t}: directory is empty")
        for p in paths:
            with open(p, "rb") as fh:
                check_member(p, fh.read(), p)
    for n in notes:
        print("  ok  ", n)
    for p in problems:
        print("PROBLEM", p)
    print(f"{len(problems)} problem(s) found" if problems else "no problems found (format checks only; "
          "engineering correctness is not checked)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
