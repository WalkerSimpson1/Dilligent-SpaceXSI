# Technical design

## Architecture

```text
Input folder → Parse and reconcile → Index records → Resolve customer once per alert
                                   → Index hits and search → Collect hit facts
Customer candidates + hit facts → Evaluate policy per candidate → Combine verdicts
                                → Render and verify graded output
                                → Explain reviews in an optional viewer
```

Use the same evaluator for batch decisions, tests, and hypothetical reviewer previews. Snapshot the input tables for a run. Load each table once, reuse customer results across hits, and index search by query. Keep duplicate lookup keys in lists. Compare results using stable, exact identifiers. For candidate searches without links, use indexes that preserve every record permitted by the final matching rules, or scan the narrowed rows with a complete matcher. An exact-name-only index would miss permitted variants. Check any optimization against an exhaustive reference on a representative development subset and synthetic edge cases. [Requirements](requirements.md)

## Records passed between components

| Record | Minimum contents |
|---|---|
| **Source reference** | Table, exact source ID where present, field, and an optional character span or join path. Source rows without official IDs can be traced internally by their keys and position. |
| **Observed fact** | Entity or customer candidate it describes, fact type, value as supplied, normalized value or interpretations, precision, source reference, eligibility for its intended use, and reason for any uncertainty. |
| **Customer candidate** | Exact customer IDs in one supported identity group, the link that found it, any links that merged it, and facts collected from those records. |
| **Comparison** | Rule, state (`SATISFIED`, `CONTRADICTED`, or `UNRESOLVED`), deciding observations, alternative values or cases checked, and any obstacle. In the individual date comparator, use `AGREES`, `CONTRADICTS`, and `INCONCLUSIVE` to describe the relationship between dates. |
| **Candidate outcome** | Candidate ID, verdict, applicable official reasons, and the observations that establish those reasons. For reviews, include the failed or unresolved predicates that matter. |
| **Hit decision** | Alert and hit IDs, candidate outcomes, combined verdict, selected reason, supporting source IDs, and optional reviewer findings. |

Eligibility is specific to the operation. A CRM name can select the customer and an approved legal name can decide whether the name contradicts the hit. An eligible search result gives evidence about the hit’s DOB. It cannot invent a new country to establish its own eligibility. An unverified DOB can help an analyst locate a better source while staying outside the deciding facts.

## 1. Validate the inventory and preserve evidence

1. Read the official JSONL tables or explicitly select the local CSV adapter. Parse IDs as strings. Preserve original blanks, declared values, lists, and multiline text. Preserve ordering when it carries meaning, such as the first listing category. Treat date-like strings as data until the date parser interprets them.
2. Reconcile alert hit lists with the hit-to-alert relationship when both are present. Check duplicates on true record identifiers and allow collisions on lookup keys. Verify each expected hit key has one attributable alert. An unreadable or contradictory hit inventory fails the run with a useful diagnostic. A broken link to an individual evidence record can stay a case-level issue, with dependent predicates unresolved.
3. In the CSV adapter, split semicolon-separated columns according to their field conventions and preserve commas inside addresses, names, and dates. Test real quoted newline handling and date/string round trips with synthetic exports. Keep truncated text or unsupported populated values visible during validation. If a known truncation or parse gap could hide a decision-changing alternative, withhold the dependent rule. Ordinary blank fields remain unknown.
4. Write graded rows to a temporary output, validate all hit keys, reason-code pairs, JSON types, and citations, then replace the intended file after success. Report structural errors with counts and locations. In development, explicitly label the CSV run and any provisional score. [Workbook introduction and format caveat](../../../datasets/datasetss.csv)

## 2. Find the customer and keep plausible alternatives

| Situation | Procedure |
|---|---|
| Direct reference | Look up alert `account_ref`, `login_handle`, or email. Walk accounts to `Customers.record_id`. Keep every record the link genuinely reaches. If links conflict, preserve their origin and apply the prescribed screened details to disambiguate. |
| Several linked records | Use the screened name and applicable screened DOB, residence/nationality, and city checks. Keep distinct candidates that still fit. Partial-date selection uses equality of the known overlapping parts. The tolerance used to clear a hit on DOB has a different purpose. |
| No usable direct link | Apply the policy’s screened-attribute search using full, preferred, or eligible login names, comparable DOB parts, country as residence or nationality, and city in the CRM city or address as applicable. Where the data cannot establish a qualifying customer, record the gap. Reconcile with the official policy before extending fallback to a broken explicit link. |
| Several records for one person | Build identity groups from the same phone plus the same full CRM DOB, or a common approved identity document number. Process these links transitively. Normalize phones conservatively so unknown country prefixes and empty placeholders cannot create links. Keep the witness for each merge. |
| Identity checks and notes | Join `Accounts` to `Onboarding` on both `account_id` and `customer_id`, then to checks on applicant ID. Join support and onboarding notes by attributed email. Apply qualifying onboarding verification and verified-check recency across the entire identity group. Use record IDs as a stable tie-break only when equally dated eligible checks support the same material facts. A genuine tie or undated conflict that could change a rule stays unresolved for that rule. |

Retain the joining path for the selected evidence. Exclude rejected and expired checks before indexing verified facts or linking by document number. Keep CRM facts and verified facts available for their respective policy purposes. If an approved check leaves one field missing, preserve approved values for its other fields and track any declaration used under the policy as declared. Establish company incorporation from a customer-side field only when the source documents its meaning. `onboarded_at`, account opening, and an untyped date each establish a different fact or no eligible incorporation fact.

With one resolved identity, use the directly supported CRM ID when available and a stable supported ID otherwise. With multiple distinct identities, keep each candidate’s country, age, aliases, and KYC facts separate. Evaluate first, then combine. A finding about one candidate cannot clear another. A missing customer yields `REVIEW` and `null` in this design. Check any case where the official validator or labels establish a different permitted use of a screened-only fact. [Policy principles 2–4](<../../../datasets/Screening Dev Set - browse - Policy.csv>)

## 3. Collect facts about the hit

### DOB and dated events

- Gather all DOB candidates from the first source level that supplies them under policy. Use the structured `dobs`, then eligible text in the first paragraph of profile notes, then eligible supplied search results. A populated, unreadable entry may still conceal an eligible date. Track that uncertainty before considering an apparently contradictory lower-priority fact. Keep all eligible alternatives within the chosen source level.
- A reported age `a` in year `Y` yields the candidate years `Y − a − 1` and `Y − a`. Keep them as years. Attribute the age to the listed person and require the age to be tied to a date in context. A role start, court date, spouse’s age, and date of birth are different observations.
- Normalize search queries by folding case and accents, removing punctuation, and sorting the name words. Confirm key formation against original JSONL. Match category using the primary category, then first category if primary is missing. Apply the organizer’s listing phrases exactly as specified, with normalized case and spacing. A result qualifies only when the phrase and a linked country describe the listed subject. Keep the hit-country fact and the result ID that established the tie. A category or country mentioned only for someone else in the snippet is insufficient.
- Parse qualifying English dated-report lines of the organizer’s form, such as `According to Example Register; September 10, 2025: notice issued`. Validate the calendar date and take the earliest qualifying report regardless of row or text order. Preserve line boundaries. A report date alone gives no DOB. For hit companies, use only structured `dobs` for incorporation evidence. A known death date is a distinct fact from a deceased status or an obituary’s publication date.

| Listing category | Required wording in supplied search result |
|---|---|
| Sanctions | `a sanctioned individual` |
| PEP | `a politically exposed person` |
| Enforcement | `the subject of enforcement action` |
| Adverse Media | `named in adverse media` |
| SOE | `a state-owned enterprise official` |
| Any other category | `named on a watchlist` |

### Country and name

- Build the hit country set from `countries`, nationality, citizenship, countries at the ends of addresses, and place of birth. Build each customer’s set from all merged records’ residence and nationality, the selected approved document country, and notes establishing where the customer lived. Treat territories separately and `International` and `Europe` as non-country values. Keep a list of parsing uncertainties that could change overlap. Travel, the location of a reporting outlet, and a relative’s residence supply different facts.
- Normalize all eligible names once, with traceable parts. Follow the organizer’s accent, punctuation, bracket, initial, and placeholder rules. Remove listed legal forms for companies. Use official given-name groups as specified, then the split/join and ordinary edit-distance rules. The threshold is based on the shorter part. A transposition costs two edits. Distinct parts count once, and one part can participate in only one selected match, including split/join comparisons. Look for at least two matched parts or coverage of the shorter name. Check each alias independently. Apply the customer placeholder/minimum-real-parts rule and the separate allowance for a hit’s one-part alias. [Policy principles 5, 6 and 8 and name variants](<../../../datasets/Screening Dev Set - browse - Policy.csv>)

## 4. Evaluate the contradiction that supports a clearance

Evaluate the necessary comparisons before choosing a verdict. Each downstream predicate checks the identity it is about, the source eligibility, and any known alternatives or policy exceptions. A parse error in unrelated material leaves a valid independent contradiction usable. A parse gap that could add an agreeing date or country can defeat the dependent clearance. Ordinary absent DOB, country, and alias fields remain unknown in the comparisons that need them.

| Reason | Clearance condition | Checks that prevent the wrong clearance |
|---|---|---|
| `DOB_MISMATCH` | A customer DOB and a nonempty set of admissible hit DOB candidates are available. Every candidate is contradicted under the DOB rule. | Keep year, month, and day precision separately. For an individual, year difference greater than one is a contradiction. In the same year, differing months when both are known, or differing days within the same known month, also contradict. A one-year difference alone is inconclusive. An agreeing candidate or a remaining inconclusive candidate defeats the universal contradiction. Apply the policy for incorporation dates where both company dates are established. |
| `LOCATION_MISMATCH` | Both sides have admissible country evidence and the country sets are disjoint under the policy. | Check all stipulated country sources for the candidate and hit. Resolve materially uncertain country values before relying on disjointness. When the individual’s name and DOB agree, the country discrepancy alone leads to `REVIEW`. A populated but unparsed DOB that could trigger this exception is an unresolved dependency for a geography-only clearance when the name agrees. An ordinarily blank DOB stays unknown. |
| `NAME_MISMATCH_VERIFIED` | An approved legal name disagrees with every eligible name and alias for the hit. | Compare the actual verified subject’s legal name and the complete eligible alias set. For an individual customer with fewer than two real name parts, leave name-based decisions unresolved. An unreadable populated alias that could agree defeats this clearance ground. |
| `TEMPORAL_IMPOSSIBILITY` | At the earliest qualifying report the customer was younger than 16, or the company had yet to be incorporated. | Use calendar boundaries. At 16 exactly, the age condition fails. If the supplied DOB could place the person on either side of their 16th birthday, this rule stays unresolved. Incorporation must be strictly after the report, even when incorporation dates have partial precision. |
| `DECEASED` | The eligible death date falls before the screening date. | Use the actual death date and the alert’s screening date. With only a partial date, all supported interpretations must be earlier. Death on the screening date alone fails the strict-before test. |
| `ENTITY_TYPE_MISMATCH` | Reliable entity types establish one as a person and the other as a company. | Use a documented mapping for explicit types. An unfamiliar type label or a contradictory source leaves type unresolved. A name that merely sounds like a business is insufficient. |

DOB confirmation is a separate predicate. It requires the customer birth year to be one of the admissible hit years and every known part that both sides give to agree. A matching birth year can agree with a full date. A genuinely ambiguous customer date representation can support a decisive comparison only if that result survives all supported interpretations. For slash dates, use a documented source convention when available. Avoid silently selecting a locale when the source convention remains uncertain.

After computing the predicates, choose a rule-supported contradiction if present. Apply the name-and-DOB exception to location before this choice. If there is no qualifying contradiction, confirm a person on name and DOB, or a company on name and country, when the required agreement and contradiction checks are satisfied. Use a review when an unresolved issue could change that confirmation. Optional facts that simply have no value leave their comparisons unknown.

**Implementation decisions to verify against the original policy and validator.** For several honored contradictions, start with a stable preference for the one with the clearest direct documentation. Use a fixed code order after source quality and stable source IDs after that. Validate alternate accepted codes on practice cases. Check the organizer’s interpretation if a location exception and a separate decisive contradiction coexist, if a company has partial incorporation evidence, or if equally recent approved checks disagree. Keep those cases in explicit tests so a policy clarification changes a targeted predicate. Until clarified, require any proposed clearance in these cases to remain justified under the supported readings.

## 5. Combine, verify, and explain

- **Combine candidate outcomes.** A single candidate uses its own verdict. Distinct candidates with differing verdicts produce `AMBIGUOUS_CUSTOMER_RECORD`. Unanimous verdicts use the shared decision and `AMBIGUOUS` for the record ID. Prefer one reason supported for all candidates when possible. If unanimous candidates have different grounds, select an applicable official reason from the stable order, scope it accurately, and summarize the independent grounds. Preserve every candidate’s deciding evidence internally. Verify representative mixed-ground cases against the official validator and scoring when available.
- **Verify the proposed clearance.** Replay the selected rule for each candidate from its admissible source references and comparison inputs. Confirm that the cited sources belong to the selected pair, the required facts are present, and the proof checked the material alternatives and exceptions. A failed replay suppresses that ground and sends the decision back through the remaining legitimate grounds or to review. Use the same policy predicates for the replay to avoid maintaining two versions of the SOP. Test the predicates against independently specified expected outcomes.
- **Render the reason.** Use templates driven by the surviving facts. Cite the minimal existing IDs that establish the verdict, including a linking or search-attribution record when it decides the case. Deduplicate without changing the input IDs. For ambiguity, cite the candidate paths and different facts that drove the split. Use an ID-free field comparison only where the record has no official ID and cite the linked official records that establish it. Use stable field order and JSON encoding. Review reasons state the actual unresolved issue instead of giving stock uncertainty text.
- **Check alert coverage.** Derive alert status only after verifying the full set of hit outputs. A missing or duplicate hit is a batch integrity issue. A valid `REVIEW` or `SAME_ENTITY` keeps the alert open.

### Reviewer view

The reviewer view uses plain labels such as “Two customer records still fit,” “The search result could describe someone else,” “Two birth years are possible,” and “The dates agree and the countries differ.” These labels accompany the official reason code in the optional view. Several obstacles may coexist. Rank the one that best explains the current decision first, then show any additional issue that could still prevent a decision after it is addressed.

| Field | What the analyst sees |
|---|---|
| **Status and scope** | `REVIEW` for a specific hit, with the alert’s other hits visible if they affect alert status. |
| **What we know** | Deciding observations and readable source references, for example “Approved identity check records a 1994 birth year.” |
| **Why this stays open** | Missing fact, failed source attribution, conflicting facts, or plausible identities with different outcomes. Show material alternatives side by side when possible. |
| **What to check next** | One concrete record or field already known to the workflow, such as the DOB in the original listing, the approved document for the account holder, or proof of prior residence. If several gaps block the case, say which remain after the first check. If the available data identifies no actionable check, show the unresolved issue and leave the next step open. |
| **What the answer could change** | Optional conditional outcomes computed by replaying this hit with a hypothetical fact and the eligibility checks that would apply. Show which input changed and surface any obstacle that still remains. |

| Review obstacle | Check to suggest | What the preview can establish |
|---|---|---|
| Two customers fit and their verdicts differ | Ask for an account-holder record or approved document that distinguishes the two candidates. | Show the earlier verdict for each candidate under the assumption that the new record securely identifies them. |
| A possible DOB could overturn the clearance | Check the original listing for a full DOB or a correction that resolves the competing dates. | Recompute using the dates the proposed source actually establishes. An additional contradictory date leaves a still-eligible agreeing date in play. |
| Name and DOB agree while countries differ | Check whether a documented country of nationality, residence, or prior residence supplies overlap. | Supported overlap can resolve the geography conflict. Confirmed disjointness alone leaves the case in review. |
| The reported event may precede the customer’s 16th birthday | Check the approved full DOB or the exact date of the qualifying report, whichever is uncertain. | The age rule clears only if the resulting dates establish that the customer was under 16. Otherwise the remaining rules determine whether the hit stays open. |

**Fictional review example.** “The customer’s approved identity check gives a birth date of 12 July 1994. A search result for the same name gives 1961, but the country needed to tie the result to the listing is missing. Check the date of birth in the original listing.” Suppose the other admissible facts give neither a contradiction nor confirmation. An eligible listing DOB of 1961 as the only candidate would clear on DOB. An eligible listing DOB of 12 July 1994 would confirm the match if the names agree and the other checks still pass. An inconclusive listing or an equally plausible candidate date keeps the case subject to the normal rules, including review when neither verdict is established.

Store hypothetical evidence in a separate in-memory scenario with the proposed source and assumptions identified. Show the current and conditional outcomes together. Keep all scenario IDs, reviewer fields, and long evidence traces outside the graded JSONL. [Failure modes and acceptance cases](failure-modes.md)
