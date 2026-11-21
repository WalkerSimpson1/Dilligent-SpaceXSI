# Track 2 evaluator

This Python 3.10+ implementation runs offline with only the Python standard library. The runner, scorer, and reviewer require zero package installs. The country lookup is a bundled TSV read as plain text. The runner accepts the organizer’s JSONL layout and a separate adapter for the local browsing CSVs, and emits one grader-shaped JSON line per hit.

## Run

Run these commands from the repository root.

```sh
# Official entry point when the original delivery is available
system/run /path/to/dev output/dev.jsonl

# Reproduce the available local run
system/run --format csv datasets output/dev.jsonl
tools/score output/dev.jsonl 'datasets/Screening Dev Set - browse - Practice labels.csv'

# Compare with the same rules before optional free-text evidence extraction
system/run --format csv --structured-only datasets output/structured.jsonl
tools/score output/structured.jsonl 'datasets/Screening Dev Set - browse - Practice labels.csv'

# Run tests and the fictional review
python3 -m unittest discover -s tests -v   # includes our Step 1-3 tests
tools/review --demo

# Inspect a local hit with an optional hypothetical DOB from its original listing
tools/review datasets HIT_ID --listing-dob 1994-07-12 --listing-dob unknown
```

`run` detects the local CSV layout if the JSONL alert table is absent. Use `--format` to select a particular adapter when both are present. The JSONL input expects the eight tables identified in the brief, `POLICY.md` and `name_variants.json`. The rules implement the v3 procedure and the name tables are read from the supplied data folder. The `score` command is the only command that reads practice labels.

Outputs in `output/` are ignored by Git. The local predictions use participant-provided facts. Package predictions for submission through the organizer’s permitted route. The reviewer demonstration uses fictional records.

## How a decision gets made

`engine/s1_load.py` reconciles each alert’s hit inventory. `engine/s2_customers.py` resolves plausible customer records once per alert. It follows account, login, and email links, uses screened details where prescribed, and joins identity checks through both account and customer. Supported shared phone and full-DOB pairs and approved document numbers link records for the same person. The latest eligible verification is used for the facts it establishes. Distinct plausible customers are evaluated separately.

`engine/s3_hit_facts.py` collects hit evidence in policy order. It preserves incomplete dates and different possible birth years. The search fallback requires the hit’s category phrase and a country attributable to the listed subject. An age in a dated report can give two birth years. `engine/normalize.py` implements date, name, and country comparisons. The country table contains ISO codes and English names from the local pycountry and IANA zoneinfo data, with explicit aliases for common terms and nationalities.

`engine/s4_decide.py` records a clearance only when a permitted contradiction survives the comparisons for each plausible customer. It uses the same predicates to replay the evidence, renders the reason from the selected findings, and includes the source IDs used. If the candidate verdicts disagree, the hit stays open for review. `engine/s5_batch.py` checks keys, evidence IDs and reason-code pairs before replacing the output file. Stable input ID ordering and fixed reason selection make reruns reproducible. The reviewer can inspect the actual reasons and source IDs, then replay an explicitly hypothetical listing DOB in a separate scenario.

## Three fictional cases

| Outcome | Deciding evidence |
|---|---|
| **Clear** | An approved identity check gives Alex Morgan a birth date in 1994. The original listing gives 1961 as the only candidate birth year. The dates contradict under the policy. The result is `DIFFERENT_ENTITY` with `DOB_MISMATCH`. |
| **Match** | The original listing instead gives 12 July 1994. The customer’s verified name and DOB agree with the listing, both are linked to the United Kingdom, and the other checks pass. The result is `SAME_ENTITY` with `NAME_DOB_LOCATION_MATCH`. |
| **Review** | A same-name search result includes a birth year, but gives no country that ties it to the listing. The program keeps the hit open and suggests checking the birth date in the original listing. `tools/review --demo` shows the current review followed by all three conditional outcomes. |

## Local verification results

After merging with Steps 1-3 (docs/plan/DECISIONS.md R1-R7) the full CSV run produces 819 hit decisions across 440 alerts: 457 different-entity decisions, 121 matches and 241 reviews (Sam's evaluator alone: 447 / 112 / 260), in about 75 seconds. Runs from different working directories produce byte-identical JSONL. 117 tests pass (Sam's synthetic acceptance cases, the Step 1-3 unit tests and the merge tests). The table below is from the evaluator before the merge; after it, the full evaluator still scores 50 of 50 with 0 unsafe clearances and 49 of 50 reference evidence sets.

| Practice-set measure | Structured-only baseline | Full evaluator |
|---|---:|---:|
| Correct decisions | 36 of 50 | 50 of 50 |
| Correct clearances | 23 of 28 | 28 of 28 |
| Unsafe clearances on genuine matches | 1 | 0 |
| Unsafe clearances on expected reviews | 4 | 0 |
| Decision cost | 323 | 0 |

Among the 50 correct decisions, all 50 used an accepted reason code and customer ID. Forty-seven included all the evidence IDs listed by the practice reference. Two of the three differences involve shared-phone records with ambiguous slash dates. The engine keeps competing date interpretations when it cannot establish an exact full DOB for merging. The other difference concerns a verification note in an ambiguous-customer review. The local scores describe the supplied practice labels only.

## Verification boundaries

The local CSV workbook can truncate long text. Its field types and layout are adaptations of the organizer’s original case tables. Synthetic tests exercise both adapters, but a conformance check with the original development and unseen deliveries requires access to those files. The official validator was absent from this checkout. The practice scorer reports decision costs and reference reason, customer ID, and evidence coverage. It cannot assess prose or substitute for official scoring.

Free-text extraction favors attributable facts and recognizable date and verification wording. An unparsed populated value can keep a rule unresolved. Ambiguous slash dates retain both valid interpretations unless the input establishes one, so some plausible phone-and-date links remain separate. The original delivery should be used to confirm date conventions and the exact JSONL name-variant schema.

## Optional Grok backup

The batch runner and Vera use the offline evaluator by default. To try Grok, set `OPENROUTER_API_KEY` in your shell and enable the backup for the run. `SCREENING_GROK_MODEL` can override the default `x-ai/grok-4.20`.

```sh
SCREENING_GROK_FALLBACK=1 system/run datasets output/dev.jsonl
```

The backup runs on an individual hit still in `REVIEW` with a usable customer birth date and no parsed or structured listing birth date. It sends the listing names and first paragraph of `profile_notes` to OpenRouter. It asks for whole, verbatim quotes. Python confirms each quote appears in the paragraph, checks its subject and date wording, keeps both possible birth years for a dated age, and sends accepted evidence through the same policy rules. Promising wording that fails these checks stays in review. Unreadable birth information in a profile blocks the fallback to supplied search snippets.

The backup is limited to 60 requests per run, a 4,000-character paragraph, and a 12-second request timeout. The runner reports request, accepted-evidence, and error counts on stderr. An unavailable API or an unusable reply keeps the original review. An in-memory cache reuses replies for identical profiles within a run. The live service can vary between runs. Use offline mode when byte-for-byte repeatability is required. Verify the backup on labeled cases before enabling it in the graded run. [OpenRouter chat API](https://openrouter.ai/docs/api-reference/chat-completion) · [Grok model endpoints](https://openrouter.ai/api/v1/models/x-ai/grok-4.20/endpoints)
