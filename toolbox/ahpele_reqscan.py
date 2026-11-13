#!/usr/bin/env python3
"""AHPELE requirement scanner (stdlib only; runs inside the task container).

Finds requirement-like statements in the text corpus written by
ahpele_index.py (/tmp/ahpele/corpus) so that hard constraints are not missed:

  python3 ahpele_reqscan.py            # scan: writes /tmp/ahpele/req_candidates.md and .csv
  python3 ahpele_reqscan.py --check    # coverage: lists candidates not yet reviewed

A candidate counts as reviewed when its ID (e.g. R0042) appears in
/tmp/ahpele/requirements.csv (adopted) or /tmp/ahpele/rejected.csv (rejected,
with a reason). A whole document can be rejected by putting its path in
rejected.csv. The scanner is a recall aid: it misses requirements that live in
tables, drawings or images, and it lists many statements that are not hard
requirements. It knows nothing about any particular task.
"""
import argparse
import csv
import html
import json
import os
import re
import sys

OUT = "/tmp/ahpele"
STRONG = re.compile(
    r"\b(shall|must|is required|are required|required to|mandatory|not permitted|prohibited|shall not|"
    r"must not|may not exceed|no later than|condition of|subject to|is to|are to|(is|are)? ?limited to|"
    r"not (be )?(less|more|greater|lower|higher) than|not exceed|at least|at most|no more than|no less than|"
    r"maximum of|minimum of|is not allowed|are not allowed|will not be accepted|not acceptable)\b", re.I)
LIMIT = re.compile(
    r"(\b(not (to )?exceed|exceed(s|ing)?|maximum|minimum|max\.?|min\.?|at least|at most|no more than|"
    r"no less than|not less than|not more than|not greater than|up to|limit(ed|s)?|cap(ped)?|allowable|"
    r"permissible|permitted|threshold|tolerance|deadline|before|prior to|within|until|expires?|valid)\b|"
    r"[≤≥<>]=?|±|\+/-)", re.I)
NUMBER = re.compile(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?")
NOISE = re.compile(r"^(--- page \d+ ---|page \d+( of \d+)?|\W*)$", re.I)
MAX_LEN = 320
TAG = re.compile(r"<[^<>]{1,400}>")
# folders that usually hold general reference material (codes, standards, catalogues) rather than project documents
REFERENCE = re.compile(r"(^|/)(library|libraries|reference|references|standards?|codes?|regulations?|catalogues?|"
                       r"catalogs?|vendor|manufacturer)(/|$)", re.I)
# file names of published codes and standards (general engineering knowledge, not task-specific)
STANDARD_NAME = re.compile(
    r"^(\d+[ _-]?CFR|UFC|UFGS|UFM|ASCE|SEI|ACI|AISC|AISI|SDI|SJI|IBC|IRC|IFC[ _-]?\d|IECC|IEC|IEEE|NFPA|NEC|NESC|ISO|EN|"
    r"BS|ASTM|ASHRAE|ASME|AWS|AWWA|API|ANSI|UL|CSA|DIN|AS|NZS|TIA|FM|NEMA|OSHA|EPA|FEMA|AASHTO|MUTCD|ICC|NCHRP|"
    r"USACE|EM[ _-]\d|ETL|DoD|IS)[ _-]?\d", re.I)
DATA_TYPES = {"csv", "json"}


def load_inventory():
    try:
        with open(os.path.join(OUT, "inventory.json"), encoding="utf-8") as fh:
            return {r["path"]: r for r in json.load(fh).get("files", [])}
    except (OSError, ValueError):
        return {}


def statements(text):
    """Yield (page, statement) pairs: lines joined into sentences, table rows kept whole."""
    page, buf = 1, []
    for raw in text.splitlines():
        m = re.match(r"--- page (\d+) ---", raw.strip())
        if m:
            if buf:
                yield page, " ".join(buf)
                buf = []
            page = int(m.group(1))
            continue
        line = raw.strip()
        if NOISE.match(line):
            if buf:
                yield page, " ".join(buf)
                buf = []
            continue
        if "\t" in raw or " | " in line or line.count("  ") > 2:  # table-like row
            if buf:
                yield page, " ".join(buf)
                buf = []
            yield page, re.sub(r"\s+", " ", line)
            continue
        buf.append(line)
        if re.search(r"[.;:]$", line) or len(" ".join(buf)) > 600:
            yield page, " ".join(buf)
            buf = []
    if buf:
        yield page, " ".join(buf)


def split_sentences(s):
    parts = re.split(r"(?<=[.;])\s+(?=[A-Z(])", s)
    return [p.strip() for p in parts if p.strip()]


def scan():
    corpus = os.path.join(OUT, "corpus")
    inv = load_inventory()
    rows = []
    data_like = {d for d, r in inv.items() if r.get("type") in DATA_TYPES}
    for dp, _, fns in os.walk(corpus):
        for fn in sorted(fns):
            if not fn.endswith(".txt"):
                continue
            full = os.path.join(dp, fn)
            doc = os.path.relpath(full, corpus)[:-4]
            try:
                text = open(full, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if text.count("<") > 20 and len(TAG.findall(text[:20000])) > 20:  # XML / HTML: keep the text only
                text = html.unescape(TAG.sub(lambda m: "\n" if re.match(r"</?(p|div|tr|li|h\d|head|br|section|para)\b",
                                                                     m.group(0), re.I) else " ", text))
            seen = set()
            for page, st in statements(text):
                for s in split_sentences(st):
                    strong, limit, nums = bool(STRONG.search(s)), bool(LIMIT.search(s)), NUMBER.findall(s)
                    if not (strong or (limit and nums)) or (doc in data_like and not strong):
                        continue
                    key = s.lower()[:200]
                    if key in seen or len(s) < 12:
                        continue
                    seen.add(key)
                    score = (4 if nums else 3) if strong else 2  # 4: modal + number, 3: modal, 2: limit + number
                    rows.append({"doc": doc, "page": page, "score": score,
                                 "text": s if len(s) <= MAX_LEN else s[:MAX_LEN] + "…",
                                 "numbers": " ".join(nums[:8])})
    for r in rows:
        r["ref"] = bool(REFERENCE.search(os.path.dirname(r["doc"]))
                        or STANDARD_NAME.search(os.path.basename(r["doc"])))
    rows.sort(key=lambda r: (r["ref"], r["doc"], r["page"]))
    for i, r in enumerate(rows, 1):
        r["id"] = f"R{i:04d}"
    with open(os.path.join(OUT, "req_candidates.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "doc", "page", "score", "ref", "numbers", "text"])
        w.writeheader()
        w.writerows(rows)
    by_doc = {}
    for r in rows:
        by_doc.setdefault(r["doc"], []).append(r)
    lines = ["# Requirement candidates", "",
             f"{len(rows)} requirement-like statements in {len(by_doc)} documents (score 4: shall/must/"
             "not-more-than wording with a number; 3: the same wording without a number; 2: a limit word with a "
             "number, often context rather than a requirement). Tables, drawings and scanned pages are only partly covered: "
             "read those yourself. Status flags come from the FILE NAME; confirm which documents govern. Project "
             "documents come first; published codes and standards and documents in reference folders are listed "
             "last: the clauses that apply are the ones the project documents invoke. --check asks you to review the "
             "score 3-4 statements of project documents; use the rest when you look a requirement up.", ""]
    shown_ref = False
    for doc, rs in by_doc.items():
        if rs[0]["ref"] and not shown_ref:
            lines += ["# Reference folders (codes, standards, catalogues)", ""]
            shown_ref = True
        flags = inv.get(doc, {}).get("flags", "")
        lines.append(f"## {doc}" + (f"  [name flags: {flags}]" if flags else "") + f"  ({len(rs)})")
        for r in rs:
            lines.append(f"- {r['id']} p{r['page']} s{r['score']}: {r['text']}")
        lines.append("")
    with open(os.path.join(OUT, "req_candidates.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    key = [r for r in rows if must_review(r)]
    kdocs = {}
    for r in key:
        kdocs[r["doc"]] = kdocs.get(r["doc"], 0) + 1
    top = sorted(kdocs.items(), key=lambda kv: -kv[1])[:10]
    print(f"requirement scan: {len(rows)} candidates in {len(by_doc)} documents -> {OUT}/req_candidates.md; "
          f"{len(key)} strong candidates in project documents to review"
          + (" (" + ", ".join(f"{d}: {n}" for d, n in top) + ")" if top else ""))
    return rows


def must_review(r):
    """Requirement wording (shall, must, is to, not more than ...) in project documents."""
    return int(r["score"]) >= 3 and str(r["ref"]) not in ("True", "1")


def read_text(path):
    try:
        return open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return ""


def check(limit):
    path = os.path.join(OUT, "req_candidates.csv")
    if not os.path.exists(path):
        scan()
    with open(path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    adopted = read_text(os.path.join(OUT, "requirements.csv"))
    rejected = read_text(os.path.join(OUT, "rejected.csv"))
    if not adopted.strip():
        print(f"{OUT}/requirements.csv is missing or empty: build the requirements table first "
              "(one row per hard requirement, with the candidate IDs it comes from).")
    ids = set(re.findall(r"\bR\d{4}\b", adopted + "\n" + rejected))
    rejected_docs = {r["doc"] for r in rows if r["doc"] in rejected}
    key = [r for r in rows if must_review(r)]
    open_rows = [r for r in key if r["id"] not in ids and r["doc"] not in rejected_docs]
    open_rows.sort(key=lambda r: (-int(r["score"]), r["doc"], int(r["page"])))
    n = len(key)
    print(f"coverage: {n - len(open_rows)}/{n} strong project-document candidates reviewed "
          f"({len(ids & {r['id'] for r in rows})} IDs cited in all, {len(rejected_docs)} documents rejected whole); "
          f"{len(open_rows)} not reviewed yet. ({len(rows) - n} weaker or code/standard candidates are optional: "
          f"see {OUT}/req_candidates.md.)")
    if not open_rows:
        print("Every candidate is adopted or rejected. Also check tables, drawings and scanned pages, which the "
              "scanner does not fully cover.")
        return 0
    print("Unreviewed candidates, strongest first (add each hard requirement to requirements.csv citing its ID, or "
          "list the ID with a reason in rejected.csv):")
    for r in open_rows[:limit]:
        print(f"- {r['id']} [{r['doc']} p{r['page']} s{r['score']}] {r['text'][:220]}")
    if len(open_rows) > limit:
        by = {}
        for r in open_rows[limit:]:
            by[r["doc"]] = by.get(r["doc"], 0) + 1
        print(f"... and {len(open_rows) - limit} more: " + ", ".join(f"{d} ({c})" for d, c in sorted(by.items())))
    return 1


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="list candidates not yet adopted or rejected")
    ap.add_argument("--limit", type=int, default=60)
    ap.add_argument("--out", default=OUT, help="index folder (default /tmp/ahpele)")
    a = ap.parse_args()
    OUT = a.out
    if a.check:
        return check(a.limit)
    scan()
    return 0


if __name__ == "__main__":
    sys.exit(main())
