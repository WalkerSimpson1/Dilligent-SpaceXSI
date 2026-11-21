# Step 2: customer resolution

```python
from system.customer import build_index, resolve, resolve_all
ix  = build_index(tables)     # tables = {'alerts','customers','accounts','onboarding','kyc','notes'}: lists of dicts
res = resolve(alert_row, ix)  # -> Resolution
res.pictures                  # one CustomerPicture per distinct PERSON that fits (>1 => step 4 decides each)
res.customer_record_id()      # record id / 'AMBIGUOUS' / None (before step 4 decides per person)
```

Standard library only. `tools/eval_step2.py` is the only file that uses pandas (it loads the xlsx dump and scores against the practice labels).

## What a CustomerPicture holds (every fact carries its source ID)
- `record_ids`: every CRM record of the person (principle 3: same phone + same full DOB, or same approved document number, applied transitively)
- `names`: full / preferred / login names, plus `verified_name`
- `dobs`: `crm_dob` facts and a `verified_dob` fact
- `countries`: `residence`, `nationality`, `document` (verified document country), `lived` (from phone/email/app notes)
- `verified`: the most recent APPROVED identity evidence, from the KYC table or a kyc-channel note (principle 4). Rejected and expired checks are never used.
- `evidence_ids`: every record the facts came from

## Behaviour
- A link (account / login / email) is followed first. Joint holders are filtered by the screened name, DOB, country and city; if more than one distinct person remains, all are returned.
- No link: search the CRM (blocked by DOB year, else country) with the principle-2 tests: name agrees with the full/preferred/login name, DOB equal in every part both give, country is residence or nationality, city is in the record's city or address.
- Dev result: 50/50 practice labels (record IDs and ambiguity). All 440 alerts resolve. About 10 s for all alerts plus about 4 s to build the index.

## Needs from other steps
- `compat.py` holds stand-ins for Step 1: `name_parts`, `names_agree_parts`, `parse_partial`, `partial_equal`, `canon_country`, `countries_in_text`, `city_in`. Swap in the real versions and keep the signatures. If the real `name_variants.json` is available, call `compat.set_variants(path)`.
- `model.py` is a minimal contract. Merge it with Step 0's `model.py`.

## Judgement calls
- A single-word preferred name ("Daniel") agrees with any screened name containing that word, per principle 8's "every part of the shorter name" rule. This adds a spurious extra person to 5 dev alerts, none of which flips ambiguous vs not. To change it, filter one-part names in `ix.parts`.
- The search matches on the CRM record. The verified identity is kept on the picture for Step 4 (verified name, DOB and document country outrank the CRM).
- Account phones always equal customer phones in dev, so `USE_ACCOUNT_PHONE` makes no difference.
