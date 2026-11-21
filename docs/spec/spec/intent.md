# Intent

An alert can contain several possible matches, called hits. For each hit, decide whether the bank’s customer is the person or company described in the listing. A clearance means `DIFFERENT_ENTITY`. A **false clearance** is a clearance when the right answer is `SAME_ENTITY` or `REVIEW`. Both count as unsafe because the program would remove a case that should have stayed open.

The central design choice is to make each clearance explainable as a specific contradiction. For example, the customer’s approved identity check establishes a full birth date, and every date attributable to the listing contradicts it under the organizer’s rules. A reviewer should be able to tell whose records supplied those dates, what precision each date had, and whether any other date could agree. An attractive explanation is insufficient if the supporting records belong to a different person or the rule examined only part of the evidence.

## Objectives

1. Minimize false clearances, including cases where the evidence is genuinely insufficient.
2. Clear as many genuine false alarms as the policy and available evidence support. Include positive controls that must clear so an implementation that reviews everything cannot pass the acceptance cases.
3. Make reviews actionable. Describe the exact doubt, show what was established, and identify the record or field that could change the outcome. Show conditional outcomes when the same rules can calculate them from a specific hypothetical fact.
4. Produce the organizer’s exact batch output for every hit and make it reproducible. The batch evaluator is the first deliverable in an implementation. A reviewer view can use the same decisions once the batch path is verified.

## Why this is the priority

The v3 brief assigns a cost of 60 to a wrong clearance. The cost of reviewing a hit that could have cleared is 3. Reviewing a genuine match costs 2, and reviewing an uncertain hit costs 0. Relative to reviewing these cases, a wrong clearance therefore consumes roughly the savings from twenty correct clearances. The event weights unseen cases at 80% of the total score. Compare approaches on errors and evidence quality as well as volume cleared. [Organizer’s v3 brief](<../../brief/Screening — Brief v3 (same person or not).docx>)

The local exports contain 440 alerts and 819 hits. An initial lookup found 146 alerts without a direct link and 58 account references that return two customer records. Of 702 individual hits, 152 supply a structured birth date or year, and 118 of those supply multiple possibilities. All 10 labeled `REVIEW` hits in the 50-case practice set use `INSUFFICIENT_DATA`. Synthetic examples must cover cases the labels miss, especially multiple plausible customers who lead to different answers. [Alerts](<../../../datasets/Screening Dev Set - browse - Alerts.csv>) · [Hits](<../../../datasets/Screening Dev Set - browse - Hits.csv>) · [Practice labels](<../../../datasets/Screening Dev Set - browse - Practice labels.csv>)

## Scope and sources

The v3 brief governs the evaluator, scoring, and publication requirements. Use the original `POLICY.md` and `name_variants.json` as the authority on decision rules and name handling. The local policy CSV and workbook tables support development until the original files arrive. The workbook warns that its text can be truncated. The original JSONL and official validator were absent when this spec was written. [Workbook introduction](../../../datasets/datasetss.csv)

This design covers local batch identity comparisons and a read-only reviewer explanation. Listing categories are used to identify admissible search evidence. Business decisions about accepting a customer and external case actions are outside the evaluator contract. Public examples and demo material use fictional records.
