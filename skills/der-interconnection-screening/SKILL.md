---
name: der-interconnection-screening
description: Utility DER interconnection screens and reports - fast-track and supplemental review screens (15 % of peak, minimum load from AMI interval data), pre-application capacity reports from queue data, certified equipment lists and witness tests, case tracking. Use for DER/solar/storage interconnection review tasks.
---

# DER interconnection screening, pre-application reports and certified equipment
Frameworks: FERC SGIP (Order 2006, revised by Order 792) and state rules modelled on it (CA Rule 21, NY SIR, others).
The utility's own tariff/procedure in the record governs: cite its sections and use its thresholds where they differ.

## Fast track / initial review screens (SGIP 2.2.1; Rule 21 Initial Review has equivalents)
Eligibility: size by line voltage and distance from substation, certified equipment (Order 792 table). Screens:
radial circuit; aggregate generation on the line section (existing + queued ahead + proposed) <= 15 % of line-section
annual peak load (section bounded by automatic sectionalizing devices or end of line); spot network limits;
fault contribution <= 10 % of circuit maximum at the primary nearest the POI; protective devices <= 87.5 % of
interrupting rating; transformer/grounding configuration (effectively grounded on 4-wire primary); shared
single-phase secondary <= 20 kW, service imbalance <= 20 % of transformer rating; transient-stability areas (10 MW);
no utility upgrades required. A failure is not a rejection: offer an options meeting / supplemental review.

## Supplemental review (SGIP 2.4.4; Rule 21 Screens N, O, P)
1. Minimum load (penetration) screen: aggregate generation on the line section < 100 % of minimum load, for every
   line section bounded by automatic sectionalizing devices upstream of the POI, using 12 months of data.
   - Solar PV without storage: daytime minimum, 10:00-16:00 for fixed-tilt (08:00-18:00 for trackers, SGIP);
     all other generation (incl. PV + storage that can discharge at night): absolute minimum over all hours.
   - Aggregate = existing interconnected + queued ahead of this request + proposed, nameplate AC (or certified
     export limit / net injection if station load is served on site). Do not count generation already reflected
     in the load data (net AMI reads at PV customers); exclude later-queued and withdrawn projects. If minimum load
     cannot be determined, the results must state why.
2. Voltage and power quality: steady-state voltage held in ANSI C84.1 Range A under all conditions incl. reverse
   flow through regulators/LTCs (bidirectional/cogeneration mode), voltage fluctuation/flicker (IEEE 1453 or
   utility practice), harmonics (IEEE 519 / IEEE 1547 limits).
3. Safety and reliability: protection coordination and fuse saving, reclosing vs inverter cease-to-energize time,
   islanding risk when generation approaches load, ground-fault overvoltage, need for transfer trip, load dominated
   by few customers or concentrated near the end of line, distance from substation.
Outcome: pass all -> interconnection agreement (possibly with minor modifications). Fail any -> name the screen and
margin, and the options: modify (reduce size, certified export limit/power control), study process (system impact /
facilities study at customer cost), or withdraw. Never "pass" a failing screen by judgement; keep judgement separate.

## Minimum load from AMI / interval data (script it, show the steps)
- Units: energy per interval (kWh) -> kW = kWh x 60 / interval minutes (x4 for 15-min); MW vs kW; delivered vs
  received channels (net load = delivered - received).
- Sum meters per timestamp, then take the minimum (never sum each meter's own minimum). Window: local time,
  interval-beginning vs -ending stamps, DST duplicates/gaps, only intervals inside the window, 12 months to as-of.
- Scope: line section(s) upstream of the POI, not feeder/substation unless only that exists (say so); check meter-
  to-section mapping and abnormal configurations (load transfers).
- Data quality: zeros, blanks, flagged/estimated reads, outages, spikes are not minimum load; state how many were
  excluded and why, and give the result both ways if exclusion changes it.
- Report: minimum, its timestamp, source, interval count, generation itemised by project, ratio, margin, pass/fail.

## Supplemental review memo of record
Contents: application/queue ID, size (AC, DC, storage, export limit), feeder/line section, procedure and edition,
data used and as-of date, each screen with basis, numbers and result, disposition and applicant's next step,
assumptions, preparer and reviewer/countersignature blocks.
If an earlier memo exists (even countersigned): do not alter it. Issue a new revision that states it supersedes
"vN dated ...", lists each error or new fact (wrong window, units, line section, missing queued project, data
gap), and gives the corrected determination; it needs fresh review/countersignature before going to the applicant.

## Pre-application report / capacity request (SGIP 1.2)
- The utility supplies existing data only (no study): total capacity of the substation/bank and circuit likely to
  serve the site, existing aggregate generation, aggregate queued generation, available capacity, single vs three
  phase and distance, peak and minimum load (daytime and absolute) when available, regulators/protective devices
  between site and substation, network service, known constraints.
- Say plainly: figures are indicative, as of a stated date, not a guarantee, not a capacity reservation, and confer
  no queue position; the request is not an interconnection application; capacity is allocated by queue order when
  a complete application is filed and studied; queue changes after the date. Do not "confirm" a figure in writing.
- Available capacity = applicable limit (hosting capacity, thermal rating or screen limit stated in the record) -
  in-service generation - active queue on the same feeder/section. Count active statuses (application complete,
  in study, ISA signed, under construction, awaiting PTO) and in-service; exclude withdrawn, rejected, expired,
  cancelled, duplicates, other feeders and pre-app requests. Use AC nameplate or certified export limit (not DC);
  storage counts at its export capability. Check MW/kW columns.
- Compare the requested size with the result (exceeds -> likely study/upgrades). Correct any wrong quoted figure.

## Certified equipment and witness tests
- Certification: NRTL listing to UL 1741; SB = IEEE 1547.1-2020 tests for IEEE 1547-2018 (SA: older Rule 21);
  state lists (e.g. CEC grid-support inverters) and the utility's Certified Equipment List.
- Carriage check per site: take the equipment actually installed (commissioning checklist, nameplate photos,
  as-builts; substitutions happen) and match manufacturer, full model number incl. suffix/rating variant, firmware
  or software version, and certification standard against the CURRENT list revision as of the date (delisted,
  superseded, expired entries do not count). Application data are not evidence of what was installed.
- Not carried -> type test / certification, or field verification witnessed by the utility (IEEE 1547-2018 clause 11
  test & verification, IEEE 1547.1-2020 procedures): unintentional islanding (cease to energize within 2 s),
  voltage/frequency trip and clearing times, ride-through category settings, enter-service / reconnect delay and
  ramp, open-phase response, voltage/reactive and frequency-watt functions, export/power-control limit, disconnect
  and interlock operation, protective relay functional tests if relay-based, applied settings vs utility profile.
- Customer/installer (often with manufacturer or commissioning agent) performs; utility witnesses (a waiver is
  decided by the authority the record names). On file first: approved application/agreement,
  AHJ final, as-built single-line, site plan, settings file and firmware evidence, test procedure accepted in
  advance, data sheets and certificates, relay settings, test equipment calibration, switching order.
- Scope a batch only after removing sites already tested, waived, at PTO, withdrawn or otherwise out of it.
Case tracking: one item per action (each site test, each follow-up) with owner, due date, reference; record the
determination on the case; close only when deliverable, items and records name the same sites and figures.
