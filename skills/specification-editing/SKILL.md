---
name: specification-editing
description: How a specification writer edits and tailors construction specification sections (CSI SectionFormat PART 1/2/3, UFGS and SpecsIntact .SEC files, MasterSpec-style masters) - working from the tagged source, resolving brackets and tailoring options, the REFERENCES and SUBMITTALS paragraphs, submittal classes and approval designations, cross-references, units, coordination with drawings and calculations, and a scripted final check. Use for any task that writes, edits, tailors or reviews specification sections.
---

# Specification editing (spec writer's practice)

## 1. Work from the master source, not from a PDF printout
- When the master is available as a tagged source (SpecsIntact `.SEC` XML, word-processor master with styles),
  read and edit that source: its tags carry paragraph structure, tailoring options, notes to the specifier,
  reference and submittal entries, and unit variants that a PDF loses. Keep its structure; write the output in the
  format the instruction asks for.
- Read the notes to the specifier before editing a paragraph; they say when to keep, delete or choose an option.
  Remove all notes and resolve every bracketed choice `[ ]` and blank before issue.
- Tailor to the project: keep only options that apply (system types, voltages, products, climate, occupancy),
  and record why an option was kept or deleted when the instruction asks for a tailoring log.

## 2. Section structure (CSI SectionFormat)
- PART 1 GENERAL: summary or scope, references, definitions, submittals, quality assurance, delivery and storage,
  warranty. PART 2 PRODUCTS: materials, equipment, ratings, factory tests. PART 3 EXECUTION: examination,
  installation, field quality control and tests, closeout.
- Keep each requirement identifiable; a list in the master stays a list of separate items. Do not merge
  paragraphs that the master keeps separate.

## 3. References
- REFERENCES lists only the publications actually cited in the section text, by publisher, designation, edition
  and title; every publication cited in the text appears in REFERENCES. Check both directions with a script.
- Cite the edition the project adopts. Design criteria addressed to the designer are not contractor requirements:
  state the requirement itself in the text rather than citing a design manual.

## 4. Submittals
- List each submittal under its class (UFGS uses SD-01 Preconstruction Submittals ... SD-11 Closeout Submittals),
  with the item named the way the text that requires it names it; every "submit" in the text has a SUBMITTALS entry
  and every entry is required somewhere in the text.
- Approval designations (for example "G" for Government approval, plus a reviewer code where the project uses one)
  are assigned per item as the project's rules state, not blanket for the whole section.

## 5. Cross-references, units, coordination
- Refer to other paragraphs by paragraph title (numbers change when paragraphs are added or deleted) and to other
  sections by number and title; check every referenced section exists in the project manual.
- Use the project's unit system consistently (SpecsIntact masters carry both; keep the one the project uses).
- Coordinate with the drawings, schedules and calculations: ratings, sizes, capacities, limits and test values in the
  specification must equal the values the design calculations and drawings establish. A conflict is a finding.

## 6. Scripted final check
Write a script that, for every section, lists: unresolved brackets or notes; references cited but not listed and
listed but not cited; "submit" statements without a SUBMITTALS entry and entries without a requirement; approval
designations per item; cross-references to paragraphs or sections that do not exist; mixed units; and values that
differ from the design basis. Fix everything it reports, then re-run it.
