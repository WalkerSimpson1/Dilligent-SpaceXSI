# False-clearance failure modes and acceptance cases

Each scenario uses fictional records. Unless stated otherwise, assume customer identity is established, the alert has one hit, and other facts provide neither an independent contradiction nor enough agreement to confirm a match. Several cases check the eligibility of a single rule. Where the experiment changes a fact, run both versions. Check the verdict, reason, reachable source IDs, and the review obstacle where applicable. See [requirements](requirements.md) for expected behavior and [design](design.md) for implementation detail.

## Where to look first after a wrong clearance

| Failure | How it could create a convincing wrong answer | Evidence to inspect |
|---|---|---|
| Wrong subject | The lookup chose the first account row or merged relatives. A valid passport now appears to contradict the hit. | All direct lookup candidates, screened details that filtered them, and every identity-group link used to reach the passport. |
| Wrong source precedence | A rejected check, an older passport, or a declaration supplied the date or legal name. | The source status and date, any qualifying onboarding note, and the facts selected from the latest approved check. |
| Wrong subject in the listing evidence | An unrelated search result, relative’s birthday, or publication date was read as the hit’s DOB. | The category phrase and country attribution, the selected text span, and the source level the DOB came from. |
| Lost alternative | A parser kept the first date, a preferred spelling, or the latest address. The remaining data looks uniquely contradictory. | Raw versus parsed candidate counts, eligible aliases, all required country sources, and ambiguity retained until the rule. |
| Wrong rule | The engine treats a years-only DOB as an exact date, treats a one-year gap as a contradiction, or clears solely because countries differ despite matching name and DOB. | The date precision and clock boundary, the direction of each comparison, and exceptions evaluated before selecting the reason. |
| Wrong scope | One customer candidate, hit, or field supplied a clearance that silently propagated to the rest. | Each candidate’s independent result, all hits under the alert, and any missing output key or fallback path. |
| Misleading explanation | The verdict may happen to be right, but the reason and citations appear to establish a stronger claim than the comparison did. | The exact selected predicate, the facts that survived eligibility and replay, and which claims the reason template emitted. |

## A. Record integrity and customer identity

| Case | Setup | Expected result |
|---|---|---|
| A01 | A two-hit alert has one eligible clearance and a second hit with insufficient data. | Two rows, one clearance and one `REVIEW`. The alert stays open. |
| A02 | The alert references an unknown hit, repeats an ID, or the hit points back to a conflicting alert. | Reject an inconsistent inventory and publish no partial file. Preserve an existing verified output if the new run fails. |
| A03 | Identical account lookup keys reach two customers. Their approved evidence leads to a match for one and clearance for the other. | `REVIEW` with `AMBIGUOUS_CUSTOMER_RECORD` and `AMBIGUOUS`. Both paths appear in the trace. Reversing table order preserves the result. |
| A04 | Two distinct candidates each rule out the hit, one on DOB and the other on a verified legal name. | `DIFFERENT_ENTITY` with customer ID `AMBIGUOUS`. Verify two independent grounds. The selected code must describe a valid scoped ground, and the explanation must make the different grounds visible. |
| A05 | An account returns two candidates. One fits the screened DOB and city. The other has a conflicting DOB or city. | Select the candidate established by the policy’s screened details. Cite the corresponding customer path. |
| A06 | Two people share a phone and address but have different full DOBs and different approved documents. | Keep separate identities. The relative’s date cannot clear the selected customer’s hit. Repeat with shared phone plus the same partial DOB and check that the records still stay separate. |
| A07 | Records A and B share a phone and full DOB. B and C share an approved document number. A prior country attached to C overlaps the hit. | Merge all three records into one identity. Use an exact customer ID and block a geography-only clearance. |
| A08 | Two records share a document number only because one check was rejected or expired. | Keep the identities separate unless another policy link establishes the merge. |
| A09 | The account ID happens to occur on onboarding rows for two distinct customer IDs. One applicant’s DOB would clear the wrong person. | Join on both account and customer ID. The other applicant never supplies the selected customer’s DOB. |
| A10 | A linked candidate has no provider check. An attributed onboarding note explicitly records a qualifying approved check with the relevant DOB. | Use the eligible note and cite it. In a paired case, a note saying only “uploaded a passport” provides no verified DOB. |
| A11 | A newer rejected check contradicts the hit. The latest approved check agrees with the hit. | Use the approved check. The rejected DOB cannot clear the hit. Confirm `SAME_ENTITY` when the names also agree and the other checks pass. |
| A12 | Equally recent eligible checks contain materially different DOBs, one agrees and the other contradicts. | The proposed DOB clearance stays unresolved. Reordering the checks cannot produce a clearance or a confident match. |
| A13 | A link-free alert’s name is a permitted nickname and its DOB is a year. One CRM record fits the available screened details. Another name match has a conflicting screened year. | The nickname candidate remains reachable and the conflicting record is filtered under the policy. The cleared or matched decision cites the selected record’s evidence. |
| A14 | The alert has no resolved customer. Its typed birthday appears to differ from the hit. | Initial design returns `REVIEW`, `INSUFFICIENT_DATA`, and null customer ID. The reason identifies the unresolved customer record. |

## B. Source attribution and reading the evidence

| Case | Setup | Expected result |
|---|---|---|
| B01 | A supplied search result matches the query and gives a much older DOB, but it describes adverse media for a sanctions hit. | Exclude the result from DOB comparison. Review if the remaining evidence cannot settle the case. Show the category mismatch in the optional trace. |
| B02 | A result matches the query, category, and a country personally tied to the listed subject. The eligible year differs from the customer’s by 30 years. Earlier source levels give no DOB. | `DIFFERENT_ENTITY` with `DOB_MISMATCH`. Cite the hit, result, customer DOB source, and any other deciding record. |
| B03 | The snippet mentions the right country only as the newspaper’s location or the subject’s relative’s residence. | The result fails country attribution. Its DOB supplies no clearance. |
| B04 | The hit has structured DOB evidence compatible with the customer. A search snippet gives a much older year. | Structured evidence controls the DOB comparison. The snippet supplies no clearance. A paired version with admissible first-paragraph DOB and empty structured DOB also takes precedence over search. |
| B05 | The first paragraph names the person’s spouse as aged 45. The listed subject’s age is absent. | The spouse’s age yields no DOB for the hit. |
| B06 | The approved customer DOB is in 1974. The hit notes describe the listed person as aged 45 in March 2019. | Preserve 1973 and 1974. `DOB_MISMATCH` fails. With compatible names and no conflicting evidence, the 1974 candidate can support `SAME_ENTITY`. |
| B07 | A structured or higher-precedence DOB list contains a contradictory date and a second populated token whose date cannot be parsed. | Retain the parsing uncertainty. A DOB-only clearance is unresolved. The review trace identifies the populated field to inspect. |
| B08 | A multiline profile includes an eligible DOB in its first paragraph. A semicolon occurs inside an unrelated field and quoted addresses contain commas. | After CSV ingestion, the DOB and paragraph boundary survive and address tokens retain their field meaning. The corresponding synthetic JSONL run produces the same decision. |
| B09 | The optional result lacks a qualifying country and could be a namesake. A separate admissible report clearly establishes that the customer was under 16. | The search issue is visible if relevant. The established `TEMPORAL_IMPOSSIBILITY` survives the unrelated DOB source problem. |
| B10 | The hit’s primary category differs from the first item in the category list. The snippet fits only that first category. | The snippet is ineligible while primary category is present. In the paired case with primary missing, the first category supplies the required phrase. |

## C. Rule boundaries and missing alternatives

| Case | Setup | Expected result |
|---|---|---|
| C01 | Customer DOB 1994-07-12 versus hit birth year 1994, names compatible. | `SAME_ENTITY` if the remaining checks pass. The reason describes evidence at its actual precision. |
| C02 | Customer birth year 1994 versus hit birth year 1995. | DOB is inconclusive. Absent any other ground, return `REVIEW`. Change the hit year to 1996 and the DOB rule clears. |
| C03 | Customer DOB 1994-07-12 versus hits with candidate dates 1961 and 1994-07-13. Then add 1994 as a third candidate. | The first version clears on DOB. The added agreeing year defeats that clearance. With names agreeing and remaining checks passing, the second version can match. |
| C04 | Customer DOB 1994-07-12 versus hit DOB 1994-08, and separately 1994-07. | Different known months contradict in the first case. A shared year and month agree in the second case. |
| C05 | A slash date could mean 5 April or 4 May under the supplied source conventions. An admissible hit has 5 April in that year. | The program cannot clear by silently choosing 4 May. Check the documented format or leave the dependent outcome unresolved. |
| C06 | The customer’s residence differs from the hit’s, but the customer’s nationality, approved document country, or a confirmed former residence overlaps a country tied to the hit. | Block location clearance in each variant. Test every stipulated country source, including a country appearing only at the end of a hit address. |
| C07 | The only geographic text on one side is blank, `International`, or `Europe`. | There is no country-based contradiction from these values. With otherwise insufficient evidence, return `REVIEW`. |
| C08 | The explicit customer and hit country sets are established, nonempty, and disjoint. There is no name-and-DOB agreement and no material parsing gap. | `DIFFERENT_ENTITY`, `LOCATION_MISMATCH`. Replace the customer country with a code or demonym for the hit country and the clearance disappears. Exercise territories as distinct countries. |
| C09 | A person’s names and DOB agree but their known country sets are disjoint. Location is the only apparent disagreement. | `REVIEW`, `INSUFFICIENT_DATA`. Explain the agreement and the geographic conflict. |
| C10 | A support note says the customer visited the hit country for a weekend. In a second case, it says they lived there previously. | Travel alone supplies no historical residence under the policy. Established prior residence prevents a location clearance in the second case. |
| C11 | The verified legal name disagrees with the hit’s primary name but agrees with an eligible alias, including a permitted single-part hit alias. | A verified-name clearance fails. Exercise compatible DOB and geography in one version to confirm the match. |
| C12 | The only customer name is a declaration. In a second version the approved legal name is an initial plus a placeholder. | No verified-name clearance in either version. An otherwise matching DOB alone cannot confirm the second version by name. |
| C13 | Two eligible names agree only after a case/accent/bracket transformation, a listed variant, or a joined/split part. | The relevant variant is recognized and blocks a name-based clearance. Repeating a part cannot create a second independent matching part. |
| C14 | A token pair swaps two letters in a 4–6-letter part and has no alternate permitted match. Test a one-letter edit, a part shorter than four, and a longer part separately. | Count the swap as two edits. At the comparison level, enforce the threshold for the shorter part and exact comparison for parts shorter than four. Use a full-name fixture where the token comparison changes the verdict. |
| C15 | An approved legal name with enough real parts disagrees with each available eligible hit name and alias. | `DIFFERENT_ENTITY`, `NAME_MISMATCH_VERIFIED`. Replace the approved name with a statement that only reports a nickname and the clearance loses that ground. |
| C16 | A customer born 2004-09-10 is named in a qualifying report dated 2020-09-09. Move the report one day forward. | Under 16 in the first case and 16 exactly in the second. Only the first clears on age. A year-only DOB that spans the age boundary stays unresolved. |
| C17 | Two qualifying reports appear in reverse chronological order. A third line appears earlier but has a different format from the organizer’s prescribed evidence. | Use the earliest qualifying date. Shuffling report line order preserves the same age result. |
| C18 | A hit reports a clear death date before screening. Compare same-day death, year-only uncertainty, and status without a death date. | Only an admissible date whose supported interpretations precede screening can clear on `DECEASED`. |
| C19 | A company was demonstrably incorporated after an eligible report. In a second version the only later date is `onboarded_at`. | `TEMPORAL_IMPOSSIBILITY` in the first case. The bank onboarding date supplies no incorporation contradiction in the second. An attributed age statement for a person supplies no incorporation date for a company hit. |
| C20 | Explicit types establish a person and a company. Replace one type with an unknown value while leaving an `Ltd` suffix in a name. | First case clears with `ENTITY_TYPE_MISMATCH`. In the second, the suffix alone cannot establish that ground. |
| C21 | Company names differ only by legal form and the admissible countries overlap. | `SAME_ENTITY` with `NAME_LOCATION_MATCH` if other checks pass. A country-free variant remains unresolved by this rule. |

## D. Explanation, coverage, and stability

| Case | Setup | Expected result |
|---|---|---|
| D01 | A hit has two valid clearance grounds and several supporting records unrelated to the selected ground. | Stable reason selection, two to four sentences, precise claims, and only deciding source IDs. Every cited ID exists and belongs to the relevant comparison or linking path. |
| D02 | Two distinct identities both need review for different missing facts. | `REVIEW`, `INSUFFICIENT_DATA`, and `AMBIGUOUS`. The reason distinguishes a common decision with different obstacles from candidates whose verdicts disagree. |
| D03 | One hit has a likely namesake result. Preview supplying a clearly different listing DOB, an agreeing DOB, and an inconclusive response. | The same rules drive all previews. Explain the assumptions and show any remaining blockers. The hypothetical evidence and flags stay out of the graded JSONL and the actual result stays in review. |
| D04 | Repeat a full run, shuffle table row order without changing meaningful field ordering, and move the working directory. | Decision, reason, identifiers, and evidence are stable. Confirm identical output bytes for identical inputs. Text paragraph order, first-category order, and source precision remain intact. |
| D05 | Run with and without the practice labels file available to the scoring harness. | The evaluator output is identical. The harness alone gains or loses the ability to measure correctness. |
| D06 | Inspect a reviewed case with several obstacles, such as unverified listing DOB and incomplete customer identity. | Show the main obstacle and the remaining blocker. Previewing a valid listing date changes only that fact and cannot claim a clearance before customer identity is secured. |
| D07 | Compare a batch run with every valid hit against a staged output containing a missing row, duplicate row, invalid reason code, or invented source ID. | Structural checks catch every error before a result is accepted as complete. |

## Triage any newly observed unsafe clearance

Reconstruct the decision in order. Identify the first step that turned uncertain or ineligible material into a decisive fact. Record the hit’s expected verdict class, the rule that fired, the source path, the missing alternative or exception, and the fix. Add a small synthetic fixture that reproduces the mechanism plus a nearby case that still deserves clearance. Re-run both before accepting the fix. Report newly unsafe decisions separately from changes in the other direction, even if the aggregate score improves.
