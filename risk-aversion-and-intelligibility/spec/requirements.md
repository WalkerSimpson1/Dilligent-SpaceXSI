# Requirements

“Policy” means the organizer’s screening procedure. “Admissible” means the fact passed that procedure’s checks for source, attribution, and purpose. A fact can be useful for finding a record and still be ineligible to determine identity. [Local policy export](<../../datasets/Screening Dev Set - browse - Policy.csv>)

## Input, output, and coverage

| ID | Requirement |
|---|---|
| REQ-01 | The evaluator shall support `system/run <data folder> <output file>` from any working directory, read case data from the supplied folder, and complete within the organizer’s 30-minute limit. |
| REQ-02 | The evaluator shall preserve source IDs, original values, missing values, list boundaries, and date precision. The local CSV adapter shall use quote-aware parsing for multiline cells and field-specific list decoding. |
| REQ-03 | When the hit inventory is readable and consistent, the evaluator shall produce exactly one row for every input `(alert_id, hit_id)`, including cases the organizer may leave unscored. If the inventory cannot be reconciled, the evaluator shall report the structural error and leave the requested output free of partial results. |
| REQ-04 | When a field is blank, the evaluator shall represent it as unknown. When a populated value cannot be interpreted and could affect a policy predicate, that predicate shall remain unresolved unless the remaining evidence establishes it across the relevant possibilities. |
| REQ-05 | The evaluator shall emit exact input IDs, one official decision and matching reason code, the resolved customer ID or prescribed sentinel, a two-to-four-sentence reason, and only source IDs used for the decision. The graded row shall follow the official schema. |

## Customer identity and evidence

| ID | Requirement |
|---|---|
| REQ-06 | When an alert provides an account reference, login, or email, the evaluator shall follow its available links and retain the full set of candidate customer records. Where the policy calls for screened-attribute matching, the evaluator shall apply the policy’s name, DOB, country, and city checks. |
| REQ-07 | When linking a customer to identity checks, the evaluator shall join onboarding by both account ID and customer ID, then join checks by applicant ID. It shall attribute notes through the resolved customer’s email. |
| REQ-08 | When joining records into one person, the evaluator shall use the policy’s same-phone-plus-same-full-DOB condition or a shared approved document number, including transitive links. Partial DOBs, phone alone, and address alone provide no such link. |
| REQ-09 | When a person has multiple checks, the evaluator shall use the most recent approved check for the fields it establishes, including qualifying onboarding notes. Only approved checks may supply verified facts or document links. |
| REQ-10 | When multiple distinct customers fit, the evaluator shall compare each with the hit independently. If their decisions differ, it shall return `REVIEW` with `AMBIGUOUS_CUSTOMER_RECORD`. If they agree, it shall return the common decision. In either case it shall use `AMBIGUOUS` for the customer ID. |
| REQ-11 | When there is one resolved person with several merged records, the evaluator shall use an exact ID from that group. When no customer is resolved, the initial design shall emit JSON `null` for the ID and send the hit for review. |

## Watchlist facts and comparisons

| ID | Requirement |
|---|---|
| REQ-12 | For an individual hit, the evaluator shall gather DOB candidates in policy order from structured DOB, first-paragraph profile evidence, then eligible supplied search results where neither earlier source gives a DOB. When a dated age supports more than one birth year, it shall preserve each possibility. |
| REQ-13 | When using a supplied search result, the evaluator shall verify the normalized query, the policy’s category phrase for the hit’s primary or first category, and a country tied to the hit before using any DOB from that result. |
| REQ-14 | When interpreting time, the evaluator shall consider only qualifying dated-report lines for the earliest report. It shall require a clear age below 16, incorporation after the report, or death before screening for the applicable temporal rule. For a hit company, the structured DOB field is the incorporation source. |
| REQ-15 | When comparing DOBs, the evaluator shall track agreement, contradiction, and an inconclusive comparison separately. It shall use `DOB_MISMATCH` only when there is at least one admissible hit candidate and every candidate contradicts the customer’s admissible DOB evidence. |
| REQ-16 | When comparing countries, the evaluator shall collect the country sources specified by the policy on both sides, normalize country names, codes, and nationalities, and preserve territories as distinct entities. It shall require a known, disjoint set on each side for `LOCATION_MISMATCH` and apply the name-and-DOB agreement exception. |
| REQ-17 | When comparing names, the evaluator shall apply the policy’s handling of accents, punctuation, brackets, initials, placeholders, variants, repeated parts, split or joined parts, aliases, edit distances, and company legal forms. A verified-name clearance shall require an admissible verified name and disagreement with every eligible hit name and alias. |
| REQ-18 | When applying `ENTITY_TYPE_MISMATCH`, the evaluator shall require an established person/company distinction on both sides. Unknown or uncertain type shall leave that rule unresolved. |

## Decisions and explanations

| ID | Requirement |
|---|---|
| REQ-19 | When proposing `DIFFERENT_ENTITY`, the evaluator shall identify a policy-allowed contradiction for every plausible customer and verify the sources and conditions for each contradiction. An unavailable field shall affect only the rules that depend on it or whose exceptions it could trigger. |
| REQ-20 | When considering `SAME_ENTITY`, the evaluator shall require compatible name and DOB for a person, or compatible name and country for a company, with the policy’s contradiction checks applied. In remaining inconclusive cases, the evaluator shall return an official `REVIEW` code. |
| REQ-21 | For each decision, the evaluator shall generate the reason and evidence IDs from the same rule inputs that decided it. When several rules apply, the evaluator shall choose the reason deterministically. When distinct customer candidates agree on the verdict for different reasons, the explanation shall make the scope of the chosen reason clear. |
| REQ-22 | When presenting a review in the reviewer view, the system shall state what is known, the specific obstacle to a decision, and the next record or field to check when one is identifiable. It shall explain why a promising but ineligible source was set aside if that fact helps the analyst. |
| REQ-23 | When presenting a conditional outcome, the reviewer view shall use the same policy evaluator with an explicitly hypothetical, scoped change. Original evidence and the original decision shall remain authoritative. Each preview shall state what it assumes and preserve a review outcome if the proposed information would still leave the case unresolved. |
| REQ-24 | When deriving an alert’s status, the evaluator shall require every referenced hit to be eligible for and assigned `DIFFERENT_ENTITY` before marking the alert as cleared. For purposes of this approach, alert status is informational. |

## Validation and data handling

| ID | Requirement |
|---|---|
| REQ-25 | For identical inputs and policy, the evaluator shall repeat decisions, reason codes, customer IDs, citations, explanations, and output order. It shall validate the file against the organizer’s validator when available. |
| REQ-26 | When evaluating a change, the team shall report unsafe clearances separately for expected `SAME_ENTITY` and expected `REVIEW`, alongside correctly cleared hits, clearance precision, review rate, and the official cost where labels permit. |
| REQ-27 | The validation suite shall include synthetic positive controls and cases where a misleading record, an overlooked alternative, or a parsing boundary could lead to false clearance. Practice labels shall be read by the scoring harness only. |
| REQ-28 | The planned implementation shall keep reviewer diagnostics opt-in and outside the graded row. Public examples shall use synthetic data. The evaluator and comparison tooling shall handle participant data and predictions under the organizer’s publication rules. |

## Properties

- **Coverage.** Every valid input hit appears exactly once. A cleared alert has a complete set of cleared hits.
- **Ownership.** Every deciding fact has an admissible path to the same customer candidate or hit being compared. A candidate’s facts stay within that candidate’s identity group.
- **Witness.** Every clearance has at least one valid official contradiction for each plausible identity. Each contradiction records which alternative values were checked.
- **Uncertainty.** Blanks remain unknown. Alternative facts are kept long enough to test any rule or exception they could change. Rules independent of an unresolved field may still decide the hit.
- **Replayability.** The same facts, policy, and candidate set produce the same decision and explanation. Scoring labels and hypothetical evidence stay outside production decisions.
