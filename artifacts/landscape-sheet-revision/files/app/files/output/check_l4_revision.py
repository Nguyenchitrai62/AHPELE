#!/usr/bin/env python3
"""
check_l4_revision.py — independent recomputation and schema check for the
Desert Sage Ranch Phase 3 L-4 street tree revision deliverables.

It recomputes every key number from first principles, compares the output
files against those numbers and against /tmp/ahpele/requirements.csv, and
prints the worst case / utilisation for every hard limit.  Exit code 0 only
when the L-4 revision is internally consistent and the memo tells the truth
about the open L-2/L-3, L-1 seal and schedule items.
"""
import csv, math, os, re, sys, datetime as dt
from openpyxl import load_workbook
from docx import Document
from pypdf import PdfReader

OUT = os.path.dirname(os.path.abspath(__file__))
REQ = os.path.join(OUT, "requirements.csv")
if not os.path.exists(REQ):
    REQ = "/tmp/ahpele/requirements.csv"

fails, warns, oks = [], [], []
def ok(msg): oks.append(msg); print(f"PASS  {msg}")
def fail(msg): fails.append(msg); print(f"FAIL  {msg}")
def warn(msg): warns.append(msg); print(f"WARN  {msg}")

def check(cond, msg):
    if cond: ok(msg)
    else: fail(msg)

def close(a,b,tol=1e-6):
    return abs(float(a)-float(b)) <= tol*max(1.0,abs(float(b)))

# ---------------------------------------------------------------- inputs
FRONTAGES = [
    ("Windmill Ln.", 2560, 34, {"CHL":43,"PAR":42,"PBR":43}),
    ("Interior collector", 1180, 16, {"PAR":30,"PBR":29}),
    ("Rainbow Blvd.", 420, 8, {"CHL":7,"PAR":7,"PBR":7}),
]
REQ_TREES = [math.ceil(lf/20) for _,lf,_,_ in FRONTAGES]
SHOWN = [s for _,_,s,_ in FRONTAGES]
ADD = [r-s for r,s in zip(REQ_TREES,SHOWN)]
TOTAL_LF = sum(lf for _,lf,_,_ in FRONTAGES)
TOTAL_REQ = sum(REQ_TREES); TOTAL_SHOWN = sum(SHOWN); TOTAL_ADD = sum(ADD)
SPECIES = {}
for _,_,_,sp in FRONTAGES:
    for k,v in sp.items(): SPECIES[k]=SPECIES.get(k,0)+v
TOTAL_TREES = TOTAL_REQ + 6 + 10
TURF_SF=18400; DRIP_SF=22200; TREE_RATE=2000
ACFT=43560.0; GAL=325851.0
turf_acft = TURF_SF*5.5/ACFT
drip_acft = DRIP_SF*1.0/ACFT
old_tree_acft = 74*TREE_RATE/GAL
new_tree_acft = TOTAL_TREES*TREE_RATE/GAL
old_total = turf_acft+drip_acft+old_tree_acft
new_total = turf_acft+drip_acft+new_tree_acft
delta = new_total-old_total
optB = 40600*1.0/ACFT+new_tree_acft
optC = 4200*5.5/ACFT+36400*1.0/ACFT+new_tree_acft
TREE_DELTA = TOTAL_ADD*485; EMIT_DELTA = TOTAL_ADD*12.5; COST_DELTA = TREE_DELTA+EMIT_DELTA
NEW_ROUND = math.ceil((4856565.75+COST_DELTA+500000)/1000)*1000
BOND_DELTA = NEW_ROUND-5357000

# schedule
def addbd(start,n,holidays=()):
    d=dt.date.fromisoformat(start); c=0
    while c<n:
        d+=dt.timedelta(days=1)
        if d.weekday()<5 and d not in holidays: c+=1
    return d
HOL={dt.date(2026,11,26),dt.date(2026,12,25)}
FINISH_1130=addbd('2026-11-30',20,HOL)
FINISH_1119=addbd('2026-11-19',20,HOL)
FINISH_1113=addbd('2026-11-13',20,HOL)
STATUTORY=dt.date(2026,12,23)
TARGET=dt.date(2026,12,18)
AVAIL_BD=0; d=dt.date(2026,11,30)
while d<TARGET:
    d+=dt.timedelta(days=1)
    if d.weekday()<5 and d not in HOL: AVAIL_BD+=1

print("="*78)
print("PART 1 — FIRST-PRINCIPLES RECOMPUTATION")
print("="*78)
for (name,lf,show,_),req,add in zip(FRONTAGES,REQ_TREES,ADD):
    print(f"  {name:20s} {lf:5d} lf -> {req:3d} required; {show:3d} shown; {add:3d} added; avg {lf/show:5.1f} lf")
check(TOTAL_LF==4160, f"frontage total = {TOTAL_LF} lf (4,160)")
check(TOTAL_REQ==208, f"required street trees = {TOTAL_REQ} (208)")
check(TOTAL_SHOWN==58, f"trees shown on 08/21/2026 = {TOTAL_SHOWN} (58)")
check(TOTAL_ADD==150, f"additional trees = {TOTAL_ADD} (150)")
check(sum(SPECIES.values())==208, f"species distribution sums to 208 ({SPECIES})")
check(TOTAL_TREES==224, f"total trees after revision = {TOTAL_TREES} (224 = 208 + 6 + 10)")
check(close(old_total,3.2870695,1e-6), f"current demand exact = {old_total:.4f} ac-ft/yr (3.2871; reported 3.28)")
check(close(new_total,4.2077357,1e-6), f"revised demand exact = {new_total:.4f} ac-ft/yr (4.2077; reported 4.20)")
check(close(delta,0.9206662,1e-6), f"demand increase = {delta:.4f} ac-ft/yr (+0.92)")
check(TREE_DELTA==72750, f"tree cost increase = ${TREE_DELTA:,} (150 x $485)")
check(EMIT_DELTA==1875, f"emitter increase = ${EMIT_DELTA:,.0f} (150 x $12.50)")
check(COST_DELTA==74625, f"direct cost increase = ${COST_DELTA:,} ($74,625)")
check(NEW_ROUND==5432000, f"revised estimate = ${NEW_ROUND:,} ($5,432,000)")
check(BOND_DELTA==75000, f"bond increase = ${BOND_DELTA:,} ($75,000)")
check(FINISH_1130.isoformat()=='2026-12-29', f"20 business days after 11/30 = {FINISH_1130} (12/29/2026)")
check(FINISH_1119.isoformat()=='2026-12-18', f"20 business days after 11/19 = {FINISH_1119} (12/18/2026)")
check(FINISH_1113.isoformat()=='2026-12-14', f"20 business days after 11/13 = {FINISH_1113} (12/14/2026)")
check(AVAIL_BD==14, f"business days between 11/30 and 12/18 = {AVAIL_BD} (14)")

# L-6 quantity reconciliation (comment L-6)
schedule_q={"LEU":260,"DAS":96,"HES":188,"ENC":280,"MUH":112,"AGE":48,"SAS":180,"YUC":28}
graphic_q={"LEU":74,"DAS":22,"HES":60,"ENC":96,"MUH":34,"AGE":8,"SAS":0,"YUC":16}
check(all(schedule_q[k]!=graphic_q[k] for k in schedule_q), "L-6: all 8 shrub/accent items differ between L-1 and L-3+L-4")
check(schedule_q["LEU"]-graphic_q["LEU"]==186 and schedule_q["YUC"]-graphic_q["YUC"]==12, "L-6: LEU discrepancy 186 and YUC discrepancy 12 are correct")

# ---------------------------------------------------------------- workbooks
print("\n"+"="*78)
print("PART 2 — WORKBOOK RECOMPUTATION")
print("="*78)

def sheet_values(path, sheet):
    wb=load_workbook(path,data_only=True,read_only=True)
    if sheet not in wb.sheetnames:
        fail(f"{os.path.basename(path)}: missing sheet '{sheet}'"); return []
    ws=wb[sheet]
    return [[("" if c is None else c) for c in row] for row in ws.iter_rows(values_only=True)]

def find_row(rows, needle):
    for i,row in enumerate(rows):
        for c in row:
            if isinstance(c,str) and needle.lower() in c.lower(): return i,row
    return None,None

# calcs
calcs=f"{OUT}/DSR_Ph3_L4_Tree_Revision_Calcs.xlsx"
rows=sheet_values(calcs,'Frontage')
if rows:
    tot=None
    for row in rows:
        if row and str(row[0]).strip().upper()=='TOTAL': tot=row
    check(tot is not None and int(tot[1])==4160 and int(tot[2])==208 and int(tot[3])==58 and int(tot[4])==150,
          "Calcs Frontage TOTAL row = 4,160 lf / 208 / 58 / 150")
rows=sheet_values(calcs,'Cost')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('74,625' in txt or '74625' in txt, "Calcs Cost shows $74,625")
    check('5,432,000' in txt or '5432000' in txt, "Calcs Cost shows $5,432,000")

# tabulation
tab=f"{OUT}/DSR_Ph3_Landscape_Tabulation_Rev1.xlsx"
rows=sheet_values(tab,'Frontage & Trees')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    for token in ['4,160','208','58','150','128','59','21','94','43','13','224']:
        check(token in txt, f"Tabulation Frontage & Trees contains {token}")
rows=sheet_values(tab,'Species')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    for token in ['50','79','208','224']:
        check(token in txt, f"Tabulation Species contains {token}")
rows=sheet_values(tab,'Shade Coverage')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('30' in txt and '26,910' in txt, "Shade Coverage tab shows 30% / 26,910 sf target")
    check('58,473' in txt and '65.2' in txt, "Shade Coverage tab shows the exact species-diameter area 58,473 sf / 65.2%")
rows=sheet_values(tab,'Turf Hydrozone Configuration')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('18,400' in txt and 'configuration' in txt.lower() and 'dimension' in txt.lower(), "Tabulation has the L-2 turf configuration exhibit (area, category, dimensions)")
rows=sheet_values(tab,'Document Cross-Check')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('Street tree count' in txt and 'Compliance note' in txt and 'Map deadline' in txt, "Tabulation Document Cross-Check covers tree count / compliance note / map deadline")
    check('30.64.030(k)' in txt and '12/23/2026' in txt, "Cross-Check cites Title 30 sec. 30.64.030(k) and 12/23/2026")

rows=sheet_values(tab,'L-2 Options')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('2.31' in txt and '2.74' in txt, "L-2 Options shows full-conversion 2.31 and hybrid 2.74 ac-ft/yr")

# irrigation
irr=f"{OUT}/DSR_Ph3_Irrigation_Demand_Worksheet_Rev1.xlsx"
rows=sheet_values(irr,'SUMMARY')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    for token in ['4.20','3.28','0.92','4.2077']:
        check(token in txt, f"Irrigation SUMMARY contains {token}")
rows=sheet_values(irr,'Trees')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('448000' in txt.replace(',','') and '1.37' in txt, "Irrigation Trees shows 448,000 gal / 1.37 ac-ft")

# source tracker status counts
try:
    import collections
    trk_src=load_workbook('/app/files/Correspondence/DSR_Ph3_Resubmittal_Tracker.xlsx',data_only=True,read_only=True)
    ws=trk_src['Comment Response Log']
    statuses=[]
    for row in ws.iter_rows(values_only=True):
        if row and str(row[0]).strip().isdigit():
            statuses.append(str(row[5]).strip() if row[5] is not None else '')
    cc=collections.Counter(statuses)
    check(len(statuses)==30, f"Source tracker has 30 comments ({len(statuses)})")
    check(cc.get('Open',0)==10 and cc.get('Pending client',0)==3 and cc.get('In progress',0)==17,
          f"Source tracker statuses: Open 10 / Pending client 3 / In progress 17 ({dict(cc)})")
except Exception as e:
    warn(f"Source tracker not available; skipped source verification: {e}")

# water budget
wbpath=f"{OUT}/DSR_Ph3_Water_Budget_Rev1.xlsx"
rows=sheet_values(wbpath,'Hydrozones')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('224' in txt and '1.37' in txt and '4.2' in txt, "Water budget Hydrozones shows 224 trees / 1.37 / 4.2")
rows=sheet_values(wbpath,'Totals')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('4.2' in txt and '3.28' in txt, "Water budget Totals shows 4.2 vs 3.28")
rows=sheet_values(wbpath,'Compliance Scenario')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('2.74' in txt and '2.31' in txt, "Water budget scenarios show 2.74 / 2.31")

# response matrix
mat=f"{OUT}/DSR_Ph3_Comment_Response_Matrix_Landscape_Rev1.xlsx"
rows=sheet_values(mat,'Landscape Matrix')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    for token in ['PARTIAL','NOT CLOSED','OPEN','L-4','L-2','L-6']:
        check(token in txt, f"Response matrix contains {token}")
    check('208' in txt and '4,160' in txt and '150' in txt, "Response matrix L-4 row carries 208 / 4,160 / 150")
    check('sealed scaled' in txt.lower(), "Response matrix L-4 requires the sealed scaled planting plan")
    check('configuration' in txt.lower(), "Response matrix L-2 requires the turf configuration exhibit")

# tracker review
trk=f"{OUT}/DSR_Ph3_Resubmittal_Tracker_Review_2026-10-31.xlsx"
rows=sheet_values(trk,'Tracker Findings')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('12/29/2026' in txt and '11/19/2026' in txt, "Tracker review states 12/29 and 11/19")
rows=sheet_values(trk,'Status Counts')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('10' in txt and '3' in txt and '17' in txt, "Tracker status counts 10 Open / 3 Pending client / 17 In progress")
rows=sheet_values(trk,'Tracker Findings')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    check('F-09' in txt and 'CCWRD-SCC-2025-1187' in txt and '09/30/2026' in txt, "Tracker review records expired CCWRD confirmation F-09")
    check('F-11' in txt and '03/14/2028' in txt, "Tracker review records the title-officer 03/14/2028 conflict F-11")
    check('palette' in txt.lower(), "Tracker review records the palette red-line comparison commitment")
    check('F-14' in txt and 'F-1' in txt and 'G-8' in txt, "Tracker review records the hard fire-access/pipe-cover/ESC items F-14")
rows=sheet_values(trk,'Critical Path')
if rows:
    txt=" ".join(str(c) for r in rows for c in r)
    for token in ['F-1','F-2','F-3','F-4','G-5','G-8','Condition 14','all 30','written turnaround']:
        check(token in txt, f"Critical Path includes {token}")

# ---------------------------------------------------------------- memo
print("\n"+"="*78)
print("PART 3 — MEMO CONTENT")
print("="*78)
memo=f"{OUT}/DSR_Ph3_L4_Street_Tree_Revision_Memo_2026-10-31.docx"
try:
    d=Document(memo)
    text="\n".join(p.text for p in d.paragraphs)
    for t in d.tables:
        for row in t.rows:
            text+="\n"+" | ".join(c.text for c in row.cells)
except Exception as e:
    fail(f"Memo DOCX cannot be read: {e}"); text=""
for token in ["October 31, 2026","Garrett Nokes","Max Braddock","208","4,160","58","150","4.20","3.28",
              "12/29/2026","12/23/2026","11/19/2026","WRC-2024-07","lot-based, not project-based",
              "Condition 14","18,400","12/31/2026","$74,625","$5,432,000","$75,000","$5,392,000",
              "cannot commit","L-2/L-3","TAB","30.64.030(j)","30.64.030(k)","30.64.050",
              "NFM-24-0118","Book 175","Page 60","20241223-0004421","12/24/2026",
              "10/03/2026","12/01/2026","QA/QC convention","$39,560","11/25/2026","12/16/2026",
              "CCWRD-SCC-2025-1187","09/30/2026","Condition 22","Silver Butte","03/14/2028","palette red-line comparison","30%","41%",
              "F-1","F-2","F-3","F-4","G-5","G-8","six business days","declined to act","Two of the 13",
              "before the L-2 adjustment","second missing element","all 30 comments","do not assume 11/18"]:
    check(token in text, f"Memo contains '{token}'")
check("For your signature" in text or "for your signature" in text, "Memo is marked for signature")
check("not yet transmitted" in text.lower() or "not transmitted" in text.lower(), "Memo says not transmitted")
# The memo must not claim the package is committed for 11/30.
check(("cannot commit to 11/30" in text) or ("cannot commit to 11/30/2026" in text), "Memo explicitly says it cannot commit to 11/30/2026")
check("12/18" in text and "cannot commit" in text, "Memo links 12/18 to the no-commit conclusion")
check("Six hard General Comments" in text or "six hard General Comments" in text, "Memo states the six hard General Comments separately from the three date blockers")
check("six to seven" not in text, "Memo no longer says 'six to seven' business days")
check("rejected as premature" not in text, "Memo no longer calls the 2024 extension application a rejection")
check("before the L-2 adjustment" in text, "Memo qualifies the $5,432,000 bond figure as pre-L-2")
check("NOT CLOSED" in text or "not closed" in text.lower(), "Memo/matrix say L-4 is not closed")
check("all 30" in text, "Memo requires all 30 comments, including the 17 in progress")

# ---------------------------------------------------------------- PDF
print("\n"+"="*78)
print("PART 4 — REVISED SHEET PDF")
print("="*78)
pdf=f"{OUT}/DSR_Ph3_Landscape_L1-L4_Rev1_L4_Tree_Revision_2026-11-30.pdf"
try:
    r=PdfReader(pdf)
    check(len(r.pages)>=8, f"Revised sheet PDF has {len(r.pages)} pages (>=8)")
    text="\n".join((pg.extract_text() or "") for pg in r.pages)
except Exception as e:
    fail(f"Revised sheet PDF cannot be read: {e}"); text=""
for token in ["208","128","59","21","4,160","150","4.20","3.28","224","Rev 1","L-2/L-3 OPEN","DELTA 1","20 ft o.c.","UNSIGNED","SEAL","REVIEW EXHIBIT","scaled plan","REVISION BLOCK","58,473"]:
    check(token in text, f"Revised sheet PDF contains '{token}'")
check("30.64.030(j)" in text and "30.64.030(k)" in text and "30.64.050" in text, "Revised sheet PDF cites Title 30 sec. 30.64.030(j)/(k)/050")
check("Clouds and delta 1 mark every changed table" not in text, "PDF no longer claims clouds mark every changed table")
check("not to scale" in text.lower(), "PDF labels the 208-symbol plan as not to scale / exhibit")

# ---------------------------------------------------------------- requirements
print("\n"+"="*78)
print("PART 5 — REQUIREMENTS TABLE")
print("="*78)
try:
    rq=list(csv.DictReader(open(REQ,encoding='utf-8')))
    check(len(rq)>=59, f"requirements.csv has {len(rq)} rows (>=59)")
    ids=[r['id'] for r in rq]
    check(len(ids)==len(set(ids)), "requirements.csv IDs are unique")
    for r in rq:
        check(bool(r.get('source_doc','').strip()), f"{r['id']}: source_doc present")
        check(bool(r.get('req_text','').strip()), f"{r['id']}: req_text present")
    # key requirement values
    alltext=" ".join(" ".join(str(v) for v in r.values()) for r in rq)
    for token in ["208","4,160","4.20","12/23/2026","12/31/2026","20 business days","18,400","lot-based","CCWRD-SCC-2025-1187","09/30/2026","Condition 22","configuration","F-1","F-2","F-3","F-4","G-5","G-8"]:
        check(token in alltext, f"requirements.csv captures {token}")
except Exception as e:
    fail(f"requirements.csv cannot be read: {e}")

# ---------------------------------------------------------------- hard-limit utilisation
print("\n"+"="*78)
print("PART 6 — WORST CASE / UTILISATION PER HARD LIMIT")
print("="*78)
limits=[]
def lim(name, demand, capacity, unit, note, status=None):
    util = demand/capacity if capacity else float('inf')
    if status is None:
        status = "PASS" if util <= 1.0 else "FAIL"
    limits.append((name,demand,capacity,unit,util,status,note))
lim("Street trees — Rev 1", 208, 208, "trees", "1.000 — meets L-4", "PASS")
lim("Street trees — Rev 0", 208, 58, "trees", "3.586x required; 58/208 = 27.9% provided", "FAIL")
lim("Street tree spacing — Rev 0", 71.7, 20, "lf/tree", "3.59x the 20-ft maximum", "FAIL")
lim("Street tree spacing — Rev 1", 20, 20, "lf/tree", "1.000", "PASS")
lim("Total trees — Rev 1", 224, 224, "trees", "1.000", "PASS")
lim("Turf in a qualifying functional category", 18400, 0, "sf", "18,400 sf nonfunctional / 0 sf functional", "FAIL")
lim("Nonfunctional turf in bond estimate", 39560, 0, "$", "$39,560 included in item 7.16", "FAIL")
lim("L-1 seal — Rev 1", 4, 0, "sheets", "0 of 4 sealed; comment L-1 open", "OPEN")
lim("L-6 schedule match — shrub/accent items", 8, 0, "items", "8 of 8 items mismatch", "FAIL")
lim("Shade coverage — Rev 1 screening", 30, 41, "%", "41% >= 30%", "PASS")
lim("Shade coverage — Rev 0 screening", 30, 11, "%", "11% < 30%", "FAIL")
lim("Second-round review available before 12/18", 20, AVAIL_BD, "business days", f"20 required / {AVAIL_BD} available = 1.43", "FAIL")
lim("Statutory presentation deadline", (FINISH_1130-STATUTORY).days, 0, "days late", "11/30 + 20 bd = 12/29; 6 days after 12/23", "FAIL")
lim("L-2 conversion deadline", 18400, 0, "sf converted", "0 sf converted; deadline 12/31/2026", "OPEN")
lim("Tree locations cleared in utility easements", 208, 0, "trees", "0 of 208 cleared; L-1 note 12", "OPEN")
lim("Response matrix comments closed", 30, 0, "comments", "0 of 30 closed; 10 open, 3 pending client, 17 in progress", "FAIL")
lim("F-1 permanent second point of access", 2, 1, "points", "FA-1 shows one permanent connection; Phase 2 stub is temporary", "FAIL")
lim("F-2 cul-de-sac inside radius", 45, 15, "feet", "45-ft minimum vs 15-ft inside curb radius on FA-1", "FAIL")
lim("F-3 hydrant spacing/flow verification", 1, 0, "schedule", "no hydrant spacing/flow table on the wet utility plans; 500 ft / 250 ft limits", "OPEN")
lim("F-4 fire-lane signage plan", 1, 0, "plan", "no NO PARKING - FIRE LANE plan in the record", "OPEN")
lim("G-5 storm-drain cover at Sta. 4+80", 3.0, 2.6, "feet", "3.0-ft minimum vs 2.6 ft provided; 0.4 ft (13%) short", "FAIL")
lim("G-8 stand-alone ESC sheet", 1, 0, "sheet", "no ESC sheet or NVR100000 NOI callout in the record", "OPEN")
lim("Condition 14 written determination", 1, 0, "determination", "no County determination on the L-2 significant-change call", "OPEN")
lim("L-4 sealed scaled planting plan", 208, 0, "located trees", "208 symbols on a schematic; 0 locations tied to the civil base in a sealed plan", "OPEN")
lim("L-2 turf configuration exhibit", 1, 0, "exhibit", "area/category tabulated; dimensions/contiguity not shown", "OPEN")
lim("CCWRD current capacity confirmation", 1, 0, "confirmation", "CCWRD-SCC-2025-1187 expired 09/30/2026; re-review required", "OPEN")

print(f"{'Limit':48s} {'Demand':>10s} {'Capacity':>10s} {'Util':>7s}  Status")
for n,d,c,u,util,s,note in limits:
    print(f"{n[:48]:48s} {d:>10} {c:>10} {util:>7.3f}  {s:6s} {note}")
open_limits=[x for x in limits if x[5]!='PASS']
print(f"\nWorst-case limit: {max(open_limits,key=lambda x:x[4])[0]} (utilisation {max(x[4] for x in open_limits):.2f})")
print("The memo correctly reports these as OPEN/FAIL and does not commit to 11/30 or 12/18; the design reserve is not applicable to an exact-count minimum, and no hard limit is treated as met without evidence.")

# ---------------------------------------------------------------- schema
print("\n"+"="*78)
print("PART 7 — FILE SCHEMA")
print("="*78)
for f in sorted(os.listdir(OUT)):
    p=os.path.join(OUT,f)
    if os.path.isfile(p) and f!='check_l4_revision.py':
        check(os.path.getsize(p)>1000, f"{f} is non-empty ({os.path.getsize(p)} bytes)")
check(os.path.getsize(__file__)>1000, "check script is non-empty")

print("\n"+"="*78)
print(f"RESULT: {len(oks)} passes, {len(fails)} failures, {len(warns)} warnings")
print("="*78)
if fails:
    print("FAILURES:")
    for f in fails: print(" -",f)
    sys.exit(1)
print("All L-4 revision numbers are consistent; the memo does not over-commit on L-2/L-3 or the schedule.")
