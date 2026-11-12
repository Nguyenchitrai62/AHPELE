#!/usr/bin/env python3
"""AHPELE document indexer (runs inside the task container).

Turns a project folder into searchable plain text plus an inventory, using only
the Python standard library for DOCX, XLSX, DXF, EML, IFC, CSV and text files,
and whatever is available for PDF (pymupdf, pdfplumber/pdfminer, or the
pdftotext/pdftoppm command-line tools). Scanned PDF pages (no text layer) are
rendered to PNG at a modest resolution so they can be read as images.

Outputs (under --out, default /tmp/ahpele):
  corpus/<relative path>.txt   full extracted text of each document
  pages/<name>_p<N>.png        rendered scanned pages
  inventory.md / inventory.json  one row per file: type, size, pages/sheets,
                               extracted characters, scanned pages, revision,
                               status flags (SUPERSEDED, CANCELLED, DRAFT, ...),
                               and revision families (same document, several revs)

Generic by design: it knows file formats, never anything about a task.
Usage: python3 ahpele_index.py --root <project dir> [--out /tmp/ahpele] [--budget 400]
"""
from __future__ import annotations

import argparse
import csv
import email
import email.policy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from xml.etree import ElementTree as ET

MAX_TEXT = 2_000_000          # characters kept per document
MAX_FILE_BYTES = 300 * 2**20  # skip files larger than this
SCAN_CHARS = 25               # a PDF page with fewer extracted characters is "scanned"
MAX_RENDER_PAGES = 120        # total scanned pages rendered to PNG
RENDER_DPI = 110
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "site-packages", ".cache", "proc", "sys"}
# letters-only boundaries: "_" counts as a separator in file names (RevA_SUPERSEDED)
FLAG_RE = re.compile(r"(?<![A-Za-z])(SUPERSEDED|CANCELL?ED|VOID|DRAFT|OBSOLETE|WITHDRAWN|NOT FOR CONSTRUCTION|"
                     r"PRELIMINARY|FOR INFORMATION ONLY|REPLACED|RESCINDED)(?![A-Za-z])", re.I)
REV_RE = re.compile(r"(?:^|[_\-\s.(])(?:REV(?:ISION)?[_\-\s.]?)([A-Z]{1,2}\d?|\d{1,3})(?=$|[_\-\s.)])", re.I)
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
      "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


# ---------------------------------------------------------------- extractors
def docx_text(path):
    out = []
    with zipfile.ZipFile(path) as z:
        names = ["word/document.xml"] + sorted(n for n in z.namelist() if re.match(r"word/(header|footer|footnotes|comments)\d*\.xml", n))
        for name in names:
            if name not in z.namelist():
                continue
            root = ET.fromstring(z.read(name))
            body = root.find("w:body", NS) if name == "word/document.xml" else root
            if body is None:
                continue
            if name != "word/document.xml":
                out.append(f"\n--- {name} ---")
            for el in body:
                tag = el.tag.split("}")[1]
                if tag == "p":
                    out.append("".join(t.text or "" for t in el.iter(f"{{{NS['w']}}}t")))
                elif tag == "tbl":
                    for tr in el.iter(f"{{{NS['w']}}}tr"):
                        cells = []
                        for tc in tr.findall("w:tc", NS):
                            cells.append(" ".join("".join(t.text or "" for t in p.iter(f"{{{NS['w']}}}t"))
                                                  for p in tc.iter(f"{{{NS['w']}}}p")).strip())
                        out.append(" | ".join(cells))
                    out.append("")
    return "\n".join(out), {}


def xlsx_text(path):
    out, info = [], {}
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("s:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['s']}}}t")))
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        rels = {}
        if "xl/_rels/workbook.xml.rels" in z.namelist():
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall("rel:Relationship", NS):
                rels[r.get("Id")] = r.get("Target")
        sheets = wb.findall("s:sheets/s:sheet", NS)
        info["sheets"] = len(sheets)
        for sh in sheets:
            rid = sh.get(f"{{{NS['r']}}}id")
            target = rels.get(rid, "")
            target = target.lstrip("/")
            target = target if target.startswith("xl/") else "xl/" + target
            out.append(f"\n=== sheet: {sh.get('name')} ===")
            if target not in z.namelist():
                continue
            root = ET.fromstring(z.read(target))
            for row in root.iter(f"{{{NS['s']}}}row"):
                cells = []
                for c in row.findall("s:c", NS):
                    ref, t = c.get("r", ""), c.get("t")
                    v, f = c.find("s:v", NS), c.find("s:f", NS)
                    val = v.text if v is not None else None
                    if t == "s" and val is not None:
                        try:
                            val = shared[int(val)]
                        except (ValueError, IndexError):
                            pass
                    elif t == "inlineStr":
                        val = "".join(x.text or "" for x in c.iter(f"{{{NS['s']}}}t"))
                    if val is None and f is None:
                        continue
                    cell = f"{ref}={val if val is not None else ''}"
                    if f is not None and (f.text or "").strip():
                        cell += f" [={f.text.strip()}]"
                    cells.append(cell)
                if cells:
                    out.append("\t".join(cells))
    return "\n".join(out), info


def dxf_text(path):
    with open(path, "rb") as fh:
        head = fh.read(22)
        if head.startswith(b"AutoCAD Binary DXF"):
            return "(binary DXF: not indexed)", {}
        data = head + fh.read()
    lines = data.decode("utf-8", "replace").splitlines()
    pairs = [(lines[i].strip(), lines[i + 1].rstrip("\r")) for i in range(0, len(lines) - 1, 2)]
    out, layers, section, ent, counts = [], set(), None, None, {}

    def flush(e):
        if not e:
            return
        typ = e.get("0")
        counts[typ] = counts.get(typ, 0) + 1
        text = (e.get("3", "") + e.get("1", "")).strip()
        if typ in ("TEXT", "MTEXT", "ATTRIB", "ATTDEF") and text:
            text = re.sub(r"\\[A-Za-z][^;]*;|\\P|[{}]", " ", text)
            out.append(f"[{typ} layer={e.get('8', '')} at=({e.get('10', '?')},{e.get('20', '?')})] {text.strip()}")
        elif typ == "DIMENSION":
            out.append(f"[DIMENSION layer={e.get('8', '')} measured={e.get('42', '?')}] {text}")
        elif typ == "INSERT":
            out.append(f"[INSERT block={e.get('2', '')} layer={e.get('8', '')} at=({e.get('10', '?')},{e.get('20', '?')})]")

    for code, val in pairs:
        if code == "0":
            flush(ent)
            ent = None
            if val == "SECTION":
                section = "?"
                continue
            if val == "ENDSEC":
                section = None
                continue
            if section == "ENTITIES" or section == "BLOCKS":
                ent = {"0": val}
            if section == "TABLES" and val == "LAYER":
                ent = {"0": "LAYER"}
        elif code == "2" and section == "?":
            section = val
        elif ent is not None:
            if ent.get("0") == "LAYER" and code == "2":
                layers.add(val)
            elif code in ("1", "3"):
                ent[code] = ent.get(code, "") + val
            elif code not in ent:
                ent[code] = val
    flush(ent)
    summary = f"\n--- layers: {', '.join(sorted(layers))}\n--- entity counts: {json.dumps(counts)}\n"
    return "\n".join(out) + summary, {"layers": len(layers)}


def eml_text(path):
    with open(path, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=email.policy.default)
    out = [f"{h}: {msg.get(h, '')}" for h in ("From", "To", "Cc", "Date", "Subject")]
    attachments = []
    for part in msg.walk():
        if part.is_multipart():
            continue
        fn = part.get_filename()
        if fn:
            attachments.append(fn)
            continue
        ctype = part.get_content_type()
        if ctype in ("text/plain", "text/html"):
            try:
                body = part.get_content()
            except Exception:  # noqa: BLE001
                body = part.get_payload(decode=True).decode("utf-8", "replace")
            if ctype == "text/html":
                body = re.sub(r"<[^>]+>", " ", body)
            out.append("\n" + body.strip())
    if attachments:
        out.append("\nattachments: " + ", ".join(attachments))
    return "\n".join(out), {}


def ifc_text(path):
    counts, names = {}, []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"#\d+\s*=\s*(IFC\w+)\(", line)
            if m:
                counts[m.group(1)] = counts.get(m.group(1), 0) + 1
                if m.group(1) in ("IFCPROJECT", "IFCSITE", "IFCBUILDING", "IFCBUILDINGSTOREY", "IFCPROPERTYSET", "IFCSPACE"):
                    names.append(line.strip()[:300])
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:40]
    return "entity counts: " + json.dumps(dict(top)) + "\n" + "\n".join(names[:400]), {}


def pdf_text(path, rel, pages_dir, render_budget):
    """Returns (text, info). Renders scanned pages while render_budget[0] > 0."""
    info = {"pages": 0, "scanned_pages": []}
    texts = []
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz  # older pymupdf
        doc = fitz.open(path)
        info["pages"] = doc.page_count
        for i, page in enumerate(doc):
            t = page.get_text() or ""
            texts.append(t)
            if len(t.strip()) < SCAN_CHARS:
                info["scanned_pages"].append(i + 1)
                if render_budget[0] > 0:
                    out = os.path.join(pages_dir, f"{safe(rel)}_p{i + 1}.png")
                    page.get_pixmap(dpi=RENDER_DPI).save(out)
                    render_budget[0] -= 1
        return join_pages(texts), info
    except ImportError:
        pass
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            info["pages"] = len(pdf.pages)
            texts = [(p.extract_text() or "") for p in pdf.pages]
    except ImportError:
        if shutil.which("pdftotext"):
            r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, timeout=120)
            texts = r.stdout.decode("utf-8", "replace").split("\f")
            if texts and not texts[-1].strip():
                texts = texts[:-1]
            info["pages"] = len(texts)
        else:
            info["no_extractor"] = True
            return "", info
    for i, t in enumerate(texts):
        if len(t.strip()) < SCAN_CHARS:
            info["scanned_pages"].append(i + 1)
            if render_budget[0] > 0 and shutil.which("pdftoppm"):
                prefix = os.path.join(pages_dir, f"{safe(rel)}_p{i + 1}")
                subprocess.run(["pdftoppm", "-r", str(RENDER_DPI), "-png", "-singlefile", "-f", str(i + 1),
                                "-l", str(i + 1), path, prefix], capture_output=True, timeout=120)
                render_budget[0] -= 1
    return join_pages(texts), info


def join_pages(texts):
    return "\n".join(f"\n--- page {i + 1} ---\n{t}" for i, t in enumerate(texts))


def plain_text(path):
    with open(path, "rb") as fh:
        return fh.read(MAX_TEXT).decode("utf-8", "replace"), {}


def csv_text(path):
    text, _ = plain_text(path)
    try:
        rows = list(csv.reader(io.StringIO(text)))
        return text, {"rows": len(rows), "columns": len(rows[0]) if rows else 0}
    except csv.Error:
        return text, {}


# ---------------------------------------------------------------- helpers
def safe(rel):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", rel)[-150:]


def family_key(name):
    base = os.path.splitext(name)[0]
    base = FLAG_RE.sub("", base)
    base = REV_RE.sub("", base)
    return re.sub(r"[_\-\s.]+", "_", base).strip("_").lower()


def kind_of(path):
    ext = os.path.splitext(path)[1].lower()
    return {".pdf": "pdf", ".docx": "docx", ".xlsx": "xlsx", ".xlsm": "xlsx", ".dxf": "dxf", ".eml": "eml",
            ".ifc": "ifc", ".csv": "csv", ".txt": "text", ".md": "text", ".json": "text", ".xml": "text",
            ".yaml": "text", ".yml": "text", ".py": "text", ".png": "image", ".jpg": "image", ".jpeg": "image",
            ".gif": "image", ".webp": "image", ".tif": "image", ".tiff": "image"}.get(ext, "other")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default="/tmp/ahpele")
    ap.add_argument("--budget", type=float, default=400, help="seconds before stopping (partial index is kept)")
    ap.add_argument("--max-files", type=int, default=4000)
    a = ap.parse_args()
    t0 = time.time()
    root = os.path.abspath(a.root)
    corpus, pages = os.path.join(a.out, "corpus"), os.path.join(a.out, "pages")
    os.makedirs(corpus, exist_ok=True)
    os.makedirs(pages, exist_ok=True)
    files = []
    for dp, dns, fns in os.walk(root):
        dns[:] = sorted(d for d in dns if d not in SKIP_DIRS and not d.startswith("."))
        if os.path.abspath(dp).startswith(os.path.abspath(a.out)):
            continue
        for fn in sorted(fns):
            files.append(os.path.join(dp, fn))
    files = files[: a.max_files]
    render_budget = [MAX_RENDER_PAGES]
    rows, stopped = [], False
    for path in files:
        rel = os.path.relpath(path, root)
        kind = kind_of(path)
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        row = {"path": rel, "type": kind, "bytes": size, "chars": 0, "pages": "", "scanned": "", "rev": "",
               "flags": "", "mentions": "", "title": "", "note": ""}
        m = REV_RE.search(os.path.basename(path))
        row["rev"] = m.group(1).upper() if m else ""
        text = ""
        if time.time() - t0 > a.budget:
            stopped = True
            row["note"] = "not indexed (time budget)"
        elif size > MAX_FILE_BYTES:
            row["note"] = "too large to index"
        elif kind in ("image", "other"):
            row["note"] = "image: view with the read tool" if kind == "image" else ""
        else:
            try:
                if kind == "pdf":
                    text, info = pdf_text(path, rel, pages, render_budget)
                    row["pages"] = info.get("pages", "")
                    if info.get("no_extractor"):
                        row["note"] = "no PDF text extractor here: render pages yourself or read as images"
                    sc = info.get("scanned_pages", [])
                    if sc:
                        row["scanned"] = f"{len(sc)} ({','.join(map(str, sc[:12]))}{'…' if len(sc) > 12 else ''})"
                else:
                    text, info = {"docx": docx_text, "xlsx": xlsx_text, "dxf": dxf_text, "eml": eml_text,
                                  "ifc": ifc_text, "csv": csv_text, "text": plain_text}[kind](path)
                    if "sheets" in info:
                        row["pages"] = f"{info['sheets']} sheets"
            except Exception as exc:  # noqa: BLE001
                row["note"] = f"extract failed: {type(exc).__name__}: {str(exc)[:80]}"
        if text:
            text = text[:MAX_TEXT]
            row["chars"] = len(text.strip())
            dest = os.path.join(corpus, rel + ".txt")
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(text)
            first = next((ln.strip() for ln in text.splitlines() if len(ln.strip()) > 3 and not ln.startswith("---")), "")
            row["title"] = first[:90]
        # status in the FILE NAME is reliable; words in the text may refer to OTHER documents
        flags = set(f.upper().replace("CANCELED", "CANCELLED") for f in FLAG_RE.findall(os.path.basename(path)))
        row["flags"] = ",".join(sorted(flags))
        mentions = set(f.upper().replace("CANCELED", "CANCELLED") for f in FLAG_RE.findall(text[:3000])) - flags
        row["mentions"] = ",".join(sorted(mentions))
        rows.append(row)
    # revision families: same document under several names/revisions
    fams = {}
    for r in rows:
        if r["type"] in ("image", "other"):
            continue
        fams.setdefault((os.path.dirname(r["path"]), family_key(os.path.basename(r["path"]))), []).append(r["path"])
    families = [sorted(v) for v in fams.values() if len(v) > 1]
    with open(os.path.join(a.out, "inventory.json"), "w", encoding="utf-8") as fh:
        json.dump({"root": root, "files": rows, "revision_families": families, "partial": stopped}, fh, indent=1)
    lines = [f"# Document inventory of {root}", "",
             f"{len(rows)} files; full text under {corpus}/<path>.txt (search: grep -ril 'term' {corpus});"
             f" scanned pages rendered to {pages}/." + (" PARTIAL: time budget reached." if stopped else ""),
             "`name flags` = status words in the FILE NAME. `text mentions` = status words found in the first page"
             " text, which often refer to OTHER documents (e.g. a spec stating that an old standard is cancelled) and do"
             " NOT mean this document is void. Confirm every status in the governing specification, RFIs and"
             " correspondence.", "",
             "| path | type | pages | scanned | rev | name flags | text mentions | chars | title / note |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['path']} | {r['type']} | {r['pages']} | {r['scanned']} | {r['rev']} | {r['flags']} | "
                     f"{r['mentions']} | {r['chars']} | {(r['title'] or r['note']).replace('|', '/')} |")
    if families:
        lines += ["", "## Possible revision families (same document, several files)", ""]
        lines += ["- " + " ; ".join(f) for f in families]
    with open(os.path.join(a.out, "inventory.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    n_scan = sum(1 for r in rows if r["scanned"])
    n_flag = sum(1 for r in rows if r["flags"])
    print(f"indexed {len(rows)} files in {time.time() - t0:.0f}s: {sum(1 for r in rows if r['chars'])} with text, "
          f"{n_scan} PDFs with scanned pages ({MAX_RENDER_PAGES - render_budget[0]} pages rendered), {n_flag} flagged, "
          f"{len(families)} revision families{' (PARTIAL)' if stopped else ''}. Inventory: {a.out}/inventory.md")


if __name__ == "__main__":
    sys.exit(main())
