# For Sam: one crashing hit fails the whole graded run

**Resolved (R10).** The graded runner and Vera now use the same per-hit fallback in `Batch.decision()`. A failed evaluation or clearance replay produces `REVIEW` with `INSUFFICIENT_DATA` and cites the alert and hit IDs. The fallback keeps the resolved customer ID or `AMBIGUOUS` when resolution has already succeeded. Diagnostics report the hit ID, exception class, and fallback count. See [R10 in the decision log](docs/plan/DECISIONS.md).

## Original problem

If deciding **any single hit** raises an exception, `system/run` writes **no output file at all**. On the unseen set, one unexpected value (an odd date, a missing field, a new list shape) would take the score to zero instead of costing one review.

## Where it happens (on `main`, commit 359d058)

- `system/engine/s5_batch.py`, `Batch.rows()` (line 43): the loop `for alert_id, hit_id in self.data.inventory:` (line 45) calls `self.decision(hit_id)` with no per-hit `try`. Any exception from `Batch.evidence()` (customer resolution, `build_hit`) or from `decide()` escapes the loop.
- `system/engine/s4_decide.py` line 216: `decide()` deliberately raises `ValueError('clearance rule failed the source evidence replay')` when a clearance fails its replay.
- `system/engine/s5_batch.py`, `main()` (line 125): catches only `(OSError, ValueError)` and returns 1. Anything else (`KeyError`, `TypeError`, `AttributeError`, `IndexError`, …) ends in a traceback. In both cases `write_rows()` is never reached, so no file is written. (Not touching an existing good output is intended; writing nothing at all is the bug.)
- `system/vera/engine_bridge.py`, `decide_all()`: Vera calls `batch.decision(hit_id)` the same way, so the analyst app crashes on the same hit.

The old Step 0 pipeline handled this per hit (`system/steps/main.py`, `safe_review()` line 20). That code is now unused, but it shows the intended behaviour.

## What the fix should do

1. **Catch per hit, never clear.** Wrap each hit's evidence + decision in `try/except Exception`. On failure, emit `REVIEW` / `INSUFFICIENT_DATA` for that hit, with `customer_record_id` = `null` (or `AMBIGUOUS` / the resolved ID if customer resolution already succeeded).
2. **Keep the row valid for `verify_rows()`.** Evidence must be a non-empty list of real IDs, so use `[alert_id, hit_id]`. (`safe_review` used `[]`, which `verify_rows` rejects.) The reason must be 2–4 sentences, e.g. "The system could not evaluate this hit. It is left for an analyst to review."
3. **Treat the replay `ValueError` the same way.** A clearance that fails its own replay must become a REVIEW for that hit, not stop the run.
4. **Keep the structural failures.** An unreadable or inconsistent inventory (missing, duplicate or mismatched hits, bad output rows) must still fail the whole run without a partial file. `test_executable_is_atomic_and_working_directory_independent` (tests/test_engine/test_screening.py line 393) and acceptance cases A02/D07 depend on this. Only per-hit evaluation errors fall back.
5. **Say so on stderr.** Count the fallbacks in the summary line (e.g. `fallbacks=1`), plus the error class and hit ID. No private data, per steering/coding-standards.md.
6. **Use the same helper in Vera.** `engine_bridge.decide_all()` should use it, so Vera and `system/run` stay byte-identical.
7. **Stay deterministic.** No timestamps or exception text that varies between runs in the graded row.

## Verification

```bash
python3 -E -s -S -m unittest discover -s tests -t .
system/run datasets output/dev.jsonl
tools/score output/dev.jsonl "datasets/Screening Dev Set - browse - Practice labels.csv"
```

The 126 tests include simulated parsing and customer-resolution failures, an actual failed clearance replay, and byte-identical CLI and Vera output when one hit falls back. Existing tests cover atomic failure for invalid inventories. The full 819-hit workbook run was byte-identical to the run on `2f28f47`, with 457 clearances, 121 matches, 241 reviews, and zero fallbacks. All 50 practice decisions were correct, with zero unsafe clearances on those labels. [Regression tests](tests/test_engine/test_batch_errors.py)
