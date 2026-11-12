---
name: professional-memo
description: How to write an engineering memo, letter, reply, review response or technical note for a named recipient, judged by an expert rubric - answer first, basis from the record, every issue with owner and timing, exact scope, signature block, and a correct DOCX file. Use whenever the deliverable is a memo, letter, reply, response, review, disposition or note.
---

# Professional engineering memo

## Before writing
- Identify: who asked, who will act on the memo, the decision they must take, the "as of" date of the record, and any
  dates in the request (target date, deadline). Note what the request says is OUT of scope and leave it out.
- Gather the record: correspondence (emails, letters, RFIs), applications, studies, test reports, standards, contracts,
  tracking data in project applications. Build a dated timeline of relevant events in `/tmp/ahpele/timeline.md`.
- For each potential issue, find the exact source (document, section, date) and what it requires.
- When the request asks whether anything stands in the way (whether something can be approved, issued, energised,
  accepted, paid...), do not stop at the first favourable reading. Build a checklist of every condition that applies
  (agreements, studies, permits, tests, payments, insurance, notices, deadlines, sign-offs, open correspondence) and
  check each one against the record as of the stated date. Only conclude that nothing stands in the way after every
  condition has been checked and cited.

## Structure
1. Header: To / From / Date (use the record's "as of" date unless told otherwise) / Subject / project identifiers.
2. **Answer first**: one or two sentences that directly answer the question (yes / no / not yet, by which date), with
   the decisive reason.
3. **Basis**: the facts and requirements the answer rests on, each cited to the record (document, section, date).
4. **Open items** (one per issue): what it is; what requirement it rests on (cite it); what has to be done; who must do
   it (name the party or role, including the customer/applicant when it is theirs); whether it can be done before the
   target date and why; consequence if not.
5. Items reviewed and found acceptable, briefly, so the reader knows they were checked.
6. Scope statement: what this memo does not cover, exactly as the request defines it.
7. Recommendation / next steps with dates.
8. Signature block for the reviewing engineer if the request asks for one (name/title placeholders only where the
   request leaves the signer unnamed; never invent credentials).

## Quality rules
- Be specific: dates, amounts, ratings, section numbers, document titles. No vague hedging.
- Distinguish facts from the record, requirements, and your engineering judgement.
- Check arithmetic and dates (business days, notice periods, expiry dates) with a script.
- Do not contradict yourself between the answer and the open items.

## Producing the file
- Write DOCX with python-docx when available (`import docx`); otherwise use the word processing MCP tool if the task
  provides one, or build the file with LibreOffice (`soffice --headless --convert-to docx file.md` or `.html`).
- Use real headings and tables, not Markdown symbols inside the Word text.
- Save exactly at the path and file name the request gives; re-open the file to confirm it reads back, and run
  `python3 /tmp/ahpele/bin/ahpele_check.py <path>`.
- If the request also asks for actions in project applications (tickets, work packages, emails, calendar), do them
  too, and make their content consistent with the memo (see the workplace-apps skill).
- End with a final message that states the answer and lists every file and record you created.
