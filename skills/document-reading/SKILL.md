---
name: document-reading
description: How to read engineering project files quickly and reliably - the prebuilt document index, PDFs including scanned pages, drawings in DXF and PDF, spreadsheets with formulas, Word specifications, emails, IFC/BIM models - and how to extract numbers, units and scales without misreading. Use at the start of a task and whenever a document is hard to read.
---

# Reading engineering documents

## Start from the index
- `/tmp/ahpele/inventory.md`: every file with type, pages, scanned pages, revision, file-name status flags and revision
  families. `/tmp/ahpele/corpus/<path>.txt`: extracted text. Search: `grep -ril "keyword" /tmp/ahpele/corpus`.
- Read the brief/task file and the governing specification fully. Skim the rest with grep for the quantities you need.

## PDFs
- Text PDFs: use the corpus text; for tables, `pdfplumber` (`page.extract_tables()`) when available.
- Scanned pages (no text layer): open the pre-rendered PNG in `/tmp/ahpele/pages/`; if you need more detail, render
  only that page at higher resolution (pymupdf: `page.get_pixmap(dpi=200, clip=rect)`, or `pdftoppm -r 200 -f N -l N`).
  After reading an image, write what you learned (values, units, notes) to `/tmp/ahpele/notes.md`; do not re-read it.

## Drawings (DXF)
- With ezdxf: `doc = ezdxf.readfile(p); msp = doc.modelspace()`; text in TEXT/MTEXT/ATTRIB entities, dimensions in
  DIMENSION (`get_measurement()`), geometry in LINE/LWPOLYLINE/CIRCLE/INSERT; group by layer. Without ezdxf, the corpus
  text lists TEXT/MTEXT/DIMENSION/INSERT with layer and position.
- Check units ($INSUNITS header, title block, notes: feet vs metres vs inches) and the drawing scale before measuring.
- Tags, line numbers and equipment IDs on drawings link to schedules: join them explicitly in a table.

## Spreadsheets (XLSX)
- `openpyxl.load_workbook(p, data_only=True)` gives cached values; `data_only=False` gives formulas. The corpus shows
  both (`A1=value [=formula]`). Watch for hidden sheets, merged header rows, units in header text, totals rows.

## Word (DOCX)
- `python-docx`: paragraphs and tables (`doc.tables`). Specs are organised by Part/Article/Paragraph: cite them that way.
  Look for tracked revision notes, "Rev" in headers/footers, and referenced standards with editions.

## Email (EML)
- `email` module: headers (From/To/Date/Subject), body, attachment names. Threads: order by Date.

## IFC
- `ifcopenshell.open(p)`; `f.by_type("IfcBuilding")`, property sets via `ifcopenshell.util.element.get_psets(el)`.
  If ifcopenshell is missing from the default python, look for another interpreter (`ls /app/.venv/bin /opt/*/bin`,
  `python3 -c "import ifcopenshell"` in each) before writing STEP text by hand.

## Numbers
- Record every value with its unit and source (file, page/sheet/cell, clause). Convert units explicitly in code.
- Prefer the most recent, in-force source when values conflict; note the conflict and your resolution.
