# Step 1 — Shared matchers: main methodological decisions

Step 1 answers three small questions that every later step asks:
**do these two names match? do these two dates of birth agree or clash? which country is this?**
Code: `system/match/names.py`, `translit.py`, `dates.py`, `countries.py`. Tests: `tests/`.
Full decision log (30 entries, incl. minor ones): [`DECISIONS.md`](DECISIONS.md).

## The one rule behind every choice

Wrongly clearing a real match costs **60** points; sending a hit to review costs **2–3**.
So whenever the data is ambiguous, we pick the reading that **cannot clear a hit**.
In practice: anything that makes two people *look more alike* (an extra name match,
an extra country) is safe; anything that makes them *look different* must be certain.

## Names

1. **Non-Latin names are kept, and transliterated where a fixed table can do it reliably.**
   Each name keeps its original text plus a Latin form. Cyrillic, Greek, Armenian,
   Georgian and Japanese kana are converted letter by letter (`Армен Мкртчян` → `armen mkrtchyan`).
   Arabic, Hebrew, Chinese, Korean and Indic scripts get no Latin form (vowels are not
   written, or a dictionary is needed) and are flagged for analysts.
   *Why:* the product must work for every naming tradition, and fixed tables give the
   same answer on every run. In dev, non-Latin names only appear as extra aliases next
   to a Latin name (most often on sanctions hits).

2. **One-way rule for transliterated names.** They can count towards a match (which
   blocks a clearance) but can never be the reason two names disagree. A hit whose names
   are *all* non-Latin is never cleared on name.
   *Why:* our transliteration is a best guess; a bad guess may cost a review, never an
   unsafe clearance.

3. **Matching is generous, in the safe direction.** Beyond the policy's rules (identical,
   listed variant, typo within 1–2 edits, written together/apart), we also allow:
   - a nickname **and** a typo together (`Jonny` ~ `Johnny` ~ `John`);
   - up to **3** parts written as one, with typos (`Abdulsalaam` ~ `Abdul Salam`);
   - particles (`al`, `abu`, `bin`, `de`, `dos`) counting as normal name parts.
   *Why:* a match only ever prevents a clearance. Cost: a few extra reviews.

4. **No third-party fuzzy-matching libraries** (e.g. rapidfuzz). The brief allows only
   the standard library, and the policy defines its own exact edit-distance thresholds.

## Dates

5. **Slash dates are day-first** (`03/04/1988` = 3 April). Evidence: 6,348 dev dates have
   a first number above 12; none has a second number above 12.

6. **An ambiguous slash date counts as a mismatch only if both readings mismatch.**
   *Why:* if we misread day and month, the worst outcome is a review, never a clearance.

7. **Missing or partial is never a mismatch.** A year alone can agree with a full date;
   an invalid date (31 February) is treated as missing. Being one year apart is neither
   agreement nor contradiction (the policy's own gap), so those hits go to review.

8. **Age checks assume the oldest possible age.** "Was the customer under 16 at the
   report?" is only *yes* if it holds under every reading of partial dates.

9. **Odd birth dates are flagged, not deleted.** Customers "born" in the 1800s (9 in dev)
   get flagged for Step 4 to treat as unknown. Customers born after 2015 (1,689) are kept
   as real: each has an approved identity check with the same date.

## Countries

10. **Every country becomes one ISO code** (`Nigeria`, `NG`, `NGA`, `Nigerian` → `NG`),
    from a hand-built table of all countries. Territories keep their own code (Hong Kong,
    Jersey, Puerto Rico); England/Scotland/Wales → `GB`. "International" and "Europe"
    are not countries.

11. **A word that could mean several countries counts as all of them**
    (`Congo` → both Congos, `Korea` → both Koreas, `Georgia` → Georgia and the US).
    *Why:* an extra country can only prevent a location clearance; a missing one could
    cause an unsafe one.

12. **Notes are scanned for any country mentioned, not for set phrases.** Notes describe
    past homes in endlessly varied wording ("resided and worked in…", "based in … for
    living purposes"), and the unseen set is worded differently again. Collecting every
    country is safe on the customer side. A sentence about where someone lived that names
    no country we recognise ("used to live in Lagos") is flagged so Step 4 won't clear
    on location.

13. **Person names are removed before scanning text about that person.** Found in
    testing: "Jordan Andrew …" was read as Jordan. In web search results that is
    dangerous (a namesake's result would look like the hit's), so **Step 3 must pass the
    name** (`find_in_text(text, exclude_names=[...])`).

## How we checked it

- 70 unit tests with invented names and dates (no dev data is committed).
- Against the 50 practice labels: all 7 name-mismatch clearances, all 12 confirmed
  name matches, all 15 date-of-birth verdicts and all 40 location statements come out
  the same as the reference answers.
- On the whole dev set: every date field parses (about 125,000 values), every country
  field resolves, and every one of the 16,882 search results yields exactly one country.
