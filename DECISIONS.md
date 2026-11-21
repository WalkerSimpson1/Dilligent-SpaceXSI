# Methodological decisions (for team review)

Short plain-language summary of the main Step 1 choices: [`STEP1_METHODOLOGY.md`](STEP1_METHODOLOGY.md).

Each entry: what we decided, why, and what it costs. Guiding rule throughout:
wrongly clearing a real match costs 60, an unnecessary review costs 2-3, so every
ambiguity is resolved in the direction that does NOT clear a hit.

Status: **Decided** = agreed by the team. **Default** = made by the implementer
under that rule, not yet discussed; flag any you disagree with.

## Step 1a: names (`system/match/names.py`, `system/match/translit.py`)

| # | Decision | Status | Why / cost |
|---|---|---|---|
| N1 | **Non-Latin names are kept, never dropped.** Each name is a `NameForm`: the original text, the scripts found, a Latin form, and how it was made (`native` / `table` / `none`). | Decided | Analysts and evidence need the original. Product must work for every naming tradition. |
| N2 | **Transliteration by fixed tables only** (Cyrillic, Greek, Armenian, Georgian, Japanese kana). Arabic, Hebrew, Chinese, Korean and Indic scripts get no Latin form (`none`). | Decided | Tables are deterministic (same output every run). Arabic/Hebrew omit vowels and Chinese needs a dictionary, so a table would guess badly. Dev set: 1,292 native, 67 transliterated, 135 `none`, all of them aliases beside a Latin primary name. |
| N3 | **One-way rule:** a transliterated name can count towards agreement (which blocks a clearance) but can never be the reason for a name mismatch. A `none` name takes part in neither. A hit whose names are all non-native is never `NAME_MISMATCH_VERIFIED`. | Decided | Our transliteration is a best guess; a bad guess may cost a review, never an unsafe clearance. |
| N4 | **Non-Latin names are flagged** (`NameForm.non_latin`) so Step 4.8 / Step 7 can show the original to an analyst. | Decided | Honesty about what the system could not read. |
| N5 | **A transliterated name plus an agreeing date of birth may confirm `SAME_ENTITY`.** | Decided | A wrong confirmation costs 3 and goes to compliance anyway. |
| N6 | **Particles (al, abu, bin, de, dos, abdul…) count as normal name parts.** | Decided | Literal policy. Matching parts only block clearances, so this is the cautious direction. Customers rarely have them (abdul 62, dos 16, al/abu/bin 0). |
| N7 | **A nickname and a typo may stack** (Jonny ~ Johnny ~ John): one part matches if it is within the edit allowance of a listed variant of the other. Only one variant hop, so groups don't chain. | Decided | Goes slightly beyond the policy's wording, in the safe direction. Side effect: Yusuf ~ Jose via Josef ≈ Jose. |
| N8 | **Up to 3 neighbouring parts may be written as one** (Abdul Rahman Al ~ Abdulrahmanal); the joined form gets the normal typo allowance; it counts as one matched part. | Decided | Policy gives the 2-part example only; extending it only adds agreement. |
| N9 | **Each part is used in at most one match**; we take the largest one-to-one pairing, ties broken by coverage then fixed order. | Default | Policy: "each distinct part counts once". Exhaustive search over small names keeps it deterministic. |
| N10 | **Repeated parts count once**, so `Ali Ali` is a one-part name and agrees with `Ali Hassan` (shorter name fully matched). | Default | Literal policy. Cautious direction. |
| N11 | **Hyphens split parts; apostrophe-like marks (' ’ ʿ ʾ and the garbled �) are deleted** (Sa'id -> said, Lefèvre-Dubois -> lefevre dubois). | Default | Splitting Sa/id would create two short parts that must match exactly. |
| N12 | **Letters Unicode does not decompose are mapped by hand** (đ→d, ø→o, ł→l, ß→ss, æ→ae…); full-width letters are folded (Ｓ→S). | Default | Bug found in testing: Đặng and Søren failed to match Dang and Soren. |
| N13 | **Placeholders** = policy list + digits + FNU/LNU/NFN/NMN, NULL, NIL, TBC, TBA, DUMMY, XX…; single letters are initials. | Default | "and the like". FNU/LNU are used on US sanctions lists. Dev customers contain N/a, 0000, XXX, TEST, NA, UNKNOWN. |
| N14 | **No third-party fuzzy matching (rapidfuzz etc.).** | Default | The brief allows only standard libraries; the policy defines its own Levenshtein thresholds, which percentage scores would not reproduce. |

## Step 1b: dates (`system/match/dates.py`)

| # | Decision | Status | Why / cost |
|---|---|---|---|
| D1 | **Slash dates are day-first** (03/04/1988 = 3 April). A date like 04/13/1988 that can only be month-first is read month-first. | Default | Dev data: 6,348 customer slash dates have a first number >12, none have a second number >12. |
| D2 | **An ambiguous slash date (both numbers ≤12) keeps both readings.** Agreement uses the day-first reading only; a DOB mismatch must hold under both readings. | Default | A misread day/month can cost a review, never a clearance. Affects 4,268 customer and 2,408 KYC dates. |
| D3 | **Fuzzy hit dates:** "circa 1970" → 1970 (the 1-year tolerance covers it); "1965-1968" / "between 1965 and 1968" → each year; "1970s" → each year of the decade. | Default | None occur in dev; cheap insurance for unseen data. |
| D4 | **Invalid dates (31/02, month 13, unparseable) are missing**, never a contradiction. | Default | "Unknown stays unknown". |
| D5 | **Implausible birth dates are flagged, not dropped:** `is_plausible_dob()` is False for a date in the future or >120 years before screening. Step 4 decides whether to treat it as unknown. | Default | 9 customers are "born" 1833–1895 (typos?). Customers born 2015+ (1,689) are NOT implausible: each has an approved KYC check with the same date, so they look deliberate (temporal-impossibility cases). |
| D6 | **Under-16 check uses the oldest possible age** given partial dates; "before" checks use the latest possible date of the earlier event. | Default | A temporal clearance only when it holds under every reading. |
| D7 | **Free-text date finder ignores bare years by default** (`bare_years=True` to opt in) and lower-case "may 2019". | Default | Bare numbers in prose are often not dates. |
| D8 | **One year apart is neither agreement nor contradiction** (customer 1988, hit 1989) → REVIEW. | Policy | Principles 6 and 7 leave this gap on purpose. |

## Step 1c: countries (`system/match/countries.py`)

| # | Decision | Status | Why / cost |
|---|---|---|---|
| C1 | **Hand-built table of all ISO 3166 countries** with ISO2/ISO3 codes, English and other names, nationality words. Canonical form = ISO2. | Default | Standard library only. Every country value in dev resolves (only "International"/"Europe" do not, as the policy says). |
| C2 | **A word that may mean several countries maps to all of them** (Congo → CG+CD, Korea → KR+KP, Georgia → GE+US, Yugoslavia/USSR → successor states). | Default | Extra countries only block LOCATION_MISMATCH; a missing one could clear unsafely. |
| C3 | **England, Scotland, Wales, Northern Ireland → GB; territories keep their own code** (HK, MO, JE, GG, IM, PR, VG…). | Policy + Default | Policy: territories are their own country. UK nations are not territories. |
| C4 | **Free text: every capitalised country name, other name or nationality word counts**, plus capital abbreviations (UK, USA, UAE). Two-letter codes are trusted only in fields. | Default | Notes describe past homes in endlessly varied wording; scanning for countries instead of verb patterns survives rewording. Dev: all 2,711 residence notes and 22,575 KYC notes yield a country. |
| C5 | **When scanning text about a named person, their name is removed first** (`exclude_names`). Step 3 MUST pass it for search results. | Default | Found in testing: "Jordan Andrew …" read as Jordan, "Indiana Perez …" as the US. On search results that is unsafe (a namesake's result would count as the hit's). With names excluded, all 16,882 dev search results give exactly one country. |
| C6 | **Possessives are stripped** ("France's" → France). | Default | Bug found in testing: 443 search results had no country. |
| C7 | **An address's country = its last comma-part that is a country**; cities are not looked up. | Default | Customer addresses end in a city but every customer also has residence_country. |
| C8 | **`residence_cue_unresolved()`** flags a sentence saying where someone lived that names no resolvable country ("used to live in Lagos"). Step 4 should then not clear on location. | Default | Insurance for unseen wording; 0 such notes in dev. |

## Notes for other steps (found while building Step 1)

- **Step 3 (search results):** call `countries.find_in_text(snippet, exclude_names=[hit name, query])`, or person names like Jordan/Georgia become countries.
- **Step 3 (ages):** profile wording varies a lot ("aged 30, in November 1998", "a 30-year-old", "reached the age of 38", "was 42 years old", "Age: 55" in prison-register blocks). In register blocks it is unclear which date the age refers to ("Released On" is not necessarily the age date).
- **Step 4:** decide whether `is_plausible_dob()` == False makes a customer DOB unknown (9 dev customers born 1833–1895).

- **Step 3:** 345 of 819 hits have a blank `primary_category`; use the first of `categories` for the listing phrase (policy principle 5).
- **Steps 4.8 / 7:** non-decisive context worth showing analysts on REVIEW: matching employer vs `position_or_allegation`, ID numbers on the hit, non-Latin aliases with original text. Hit `identifiers` never coincide with KYC document numbers in dev, so they cannot confirm.
- **Policy:** only name + date of birth (person) or name + country (company) can confirm `SAME_ENTITY`.
