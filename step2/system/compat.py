"""Stand-ins for the Step 1 matchers (names / dates / countries).

Step 2 only depends on the small API at the bottom of each section. When the
real `system/match/*` modules land, replace the bodies (or re-export from them)
and keep the signatures. Standard library only.
"""
import json
import os
import re
import unicodedata

_HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# Names (SOP principle 8)
# --------------------------------------------------------------------------
_PLACEHOLDERS = {"na", "n/a", "test", "unknown", "xxx", "none"}
_TRANSLIT = str.maketrans({"ß": "ss", "ø": "o", "æ": "ae", "œ": "oe", "ł": "l",
                           "đ": "d", "ð": "d", "þ": "th", "ı": "i"})


def _load_variants(path=None):
    path = path or os.path.join(_HERE, "name_variants_fallback.json")
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    groups = d.get("given_name_groups", [])
    forms = set(x.lower() for x in d.get("company_legal_forms", []))
    part_groups = {}
    for gi, g in enumerate(groups):
        for p in g:
            part_groups.setdefault(strip_accents(p.lower()), set()).add(gi)
    return part_groups, forms


def strip_accents(s):
    s = s.translate(_TRANSLIT)
    return "".join(c for c in unicodedata.normalize("NFKD", s)
                   if not unicodedata.combining(c))


_PART_GROUPS, _LEGAL_FORMS = _load_variants()


def set_variants(path):
    """Point at the real name_variants.json shipped with the data."""
    global _PART_GROUPS, _LEGAL_FORMS
    _PART_GROUPS, _LEGAL_FORMS = _load_variants(path)


def name_parts(name, company=False):
    """Normalised distinct name parts: lowercase, no accents/punctuation/brackets,
    no single letters (initials), no placeholders, no company legal forms."""
    if not name:
        return []
    s = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", " ", str(name))
    out, seen = [], set()
    for tok in s.split():
        low = strip_accents(tok.lower()).strip(".,;:")
        if low in _PLACEHOLDERS or any(ch.isdigit() for ch in low):
            continue
        for p in re.split(r"[^a-z]+", re.sub(r"['’`]", "", low)):
            if len(p) < 2:                       # initials are not parts
                continue
            if p in _PLACEHOLDERS or (company and p in _LEGAL_FORMS):
                continue
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def _within(a, b, k):
    """Levenshtein distance <= k (insert/delete/substitute; a swap costs 2)."""
    if abs(len(a) - len(b)) > k:
        return False
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        if min(cur) > k:
            return False
        prev = cur
    return prev[-1] <= k


def part_match(a, b):
    if a == b:
        return True
    ga, gb = _PART_GROUPS.get(a), _PART_GROUPS.get(b)
    if ga and gb and (ga & gb):
        return True
    n = min(len(a), len(b))                      # shorter part's length decides
    if n < 4:
        return False
    return _within(a, b, 1 if n <= 6 else 2)


def match_count(pa, pb):
    """Greedy one-to-one matching of parts; a part written together on one side
    and apart on the other counts as ONE matched part covering both."""
    ua, ub = [False] * len(pa), [False] * len(pb)
    matched = 0
    for i, x in enumerate(pa):
        for j, y in enumerate(pb):
            if not ub[j] and part_match(x, y):
                ua[i] = ub[j] = True
                matched += 1
                break
    for i, x in enumerate(pa):                   # x == y1+y2
        if ua[i]:
            continue
        for j in range(len(pb) - 1):
            if not ub[j] and not ub[j + 1] and part_match(x, pb[j] + pb[j + 1]):
                ua[i] = ub[j] = ub[j + 1] = True
                matched += 1
                break
    for j, y in enumerate(pb):                   # y == x1+x2
        if ub[j]:
            continue
        for i in range(len(pa) - 1):
            if not ua[i] and not ua[i + 1] and part_match(y, pa[i] + pa[i + 1]):
                ub[j] = ua[i] = ua[i + 1] = True
                matched += 1
                break
    return matched, all(ua) if len(pa) <= len(pb) else all(ub)


def names_agree_parts(pa, pb):
    """Names agree when >=2 parts match, or every part of the shorter name matches."""
    if not pa or not pb:
        return False
    m, shorter_all = match_count(pa, pb)
    return m >= 2 or (shorter_all and m >= 1)


def names_agree(a, b, company=False):
    return names_agree_parts(name_parts(a, company), name_parts(b, company))


# --------------------------------------------------------------------------
# Dates (partial dates as (year, month|None, day|None))
# --------------------------------------------------------------------------
_MONTHS = {m: i + 1 for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july",
     "august", "september", "october", "november", "december"])}
_MON_RE = "|".join(_MONTHS)
DATE_RE = re.compile(
    r"(?P<iso>\b\d{4}-\d{2}-\d{2}\b)"
    r"|(?P<dmy>\b\d{1,2}/\d{1,2}/\d{4}\b)"
    r"|(?P<dMy>\b\d{1,2} (?:%s),? \d{4}\b)"
    r"|(?P<Mdy>\b(?:%s) \d{1,2}, \d{4}\b)"
    r"|(?P<iso_m>\b\d{4}-\d{2}\b)"
    r"|(?P<My>\b(?:%s) \d{4}\b)" % (_MON_RE, _MON_RE, _MON_RE), re.I)


def parse_partial(s):
    """'1988-03-14' | '14/03/1988' | '14 March 1988' | 'March 14, 1988' |
    '1988-03' | 'March 1988' | '1988' -> (y, m, d) with None for missing parts."""
    if s is None:
        return None
    s = str(s).strip()
    if not s or s.lower() == "nan":
        return None
    m = re.fullmatch(r"(\d{4})", s)
    if m:
        return (int(m.group(1)), None, None)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})", s)
    if m:
        return (int(m.group(1)), int(m.group(2)), None)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if m:
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if b > 12 >= a:                          # mm/dd/yyyy
            return (y, a, b)
        return (y, b, a)                         # dd/mm/yyyy (data convention)
    m = re.fullmatch(r"(\d{1,2}) ([A-Za-z]+),? (\d{4})", s)
    if m and m.group(2).lower() in _MONTHS:
        return (int(m.group(3)), _MONTHS[m.group(2).lower()], int(m.group(1)))
    m = re.fullmatch(r"([A-Za-z]+) (\d{1,2}), (\d{4})", s)
    if m and m.group(1).lower() in _MONTHS:
        return (int(m.group(3)), _MONTHS[m.group(1).lower()], int(m.group(2)))
    m = re.fullmatch(r"([A-Za-z]+) (\d{4})", s)
    if m and m.group(1).lower() in _MONTHS:
        return (int(m.group(2)), _MONTHS[m.group(1).lower()], None)
    return None


def partial_equal(a, b):
    """Equal in every part both give (None = part not given)."""
    if a is None or b is None:
        return True
    return all(x is None or y is None or x == y for x, y in zip(a, b))


def is_full(d):
    return d is not None and None not in d


def find_dates(text):
    """[(start, end, partial_date, raw)] for every date expression in free text."""
    out = []
    for m in DATE_RE.finditer(text):
        d = parse_partial(m.group(0))
        if d:
            out.append((m.start(), m.end(), d, m.group(0)))
    return out


# --------------------------------------------------------------------------
# Countries
# --------------------------------------------------------------------------
_COUNTRIES = {  # code: (name, demonym, other spellings)
    "AR": ("Argentina", "Argentine", []), "AT": ("Austria", "Austrian", []),
    "AU": ("Australia", "Australian", []), "BD": ("Bangladesh", "Bangladeshi", []),
    "BR": ("Brazil", "Brazilian", []), "CA": ("Canada", "Canadian", []),
    "CI": ("Cote D'Ivoire", "Ivorian", ["Côte d'Ivoire", "Ivory Coast"]),
    "CO": ("Colombia", "Colombian", []), "CZ": ("Czech Republic", "Czech", ["Czechia"]),
    "DE": ("Germany", "German", []), "DK": ("Denmark", "Danish", []),
    "DO": ("Dominican Republic", "Dominican", []), "DZ": ("Algeria", "Algerian", []),
    "AM": ("Armenia", "Armenian", []),
    "EC": ("Ecuador", "Ecuadorian", []), "ES": ("Spain", "Spanish", []),
    "FI": ("Finland", "Finnish", []), "FR": ("France", "French", []),
    "GB": ("United Kingdom", "British", ["UK", "Great Britain", "England", "Scotland", "Wales"]),
    "GH": ("Ghana", "Ghanaian", []), "HT": ("Haiti", "Haitian", []),
    "HU": ("Hungary", "Hungarian", []), "ID": ("Indonesia", "Indonesian", []),
    "IE": ("Ireland", "Irish", []), "IL": ("Israel", "Israeli", []),
    "IN": ("India", "Indian", []), "IT": ("Italy", "Italian", []),
    "JM": ("Jamaica", "Jamaican", []), "KE": ("Kenya", "Kenyan", []),
    "KP": ("North Korea", "North Korean", []), "LB": ("Lebanon", "Lebanese", []),
    "MA": ("Morocco", "Moroccan", []), "MD": ("Moldova", "Moldovan", []),
    "ME": ("Montenegro", "Montenegrin", []), "MX": ("Mexico", "Mexican", []),
    "NG": ("Nigeria", "Nigerian", []), "NL": ("Netherlands", "Dutch", ["Holland"]),
    "NO": ("Norway", "Norwegian", []), "NZ": ("New Zealand", "New Zealander", []),
    "PA": ("Panama", "Panamanian", []), "PE": ("Peru", "Peruvian", []),
    "PK": ("Pakistan", "Pakistani", []), "PL": ("Poland", "Polish", []),
    "PT": ("Portugal", "Portuguese", []), "RO": ("Romania", "Romanian", []),
    "RS": ("Serbia", "Serbian", []), "RU": ("Russia", "Russian", []),
    "SE": ("Sweden", "Swedish", []), "SG": ("Singapore", "Singaporean", []),
    "SI": ("Slovenia", "Slovenian", []), "SY": ("Syria", "Syrian", []),
    "TH": ("Thailand", "Thai", []), "CH": ("Switzerland", "Swiss", []),
    "AE": ("United Arab Emirates", "Emirati", ["UAE"]),
    "US": ("United States", "American", ["USA", "United States of America", "U.S."]),
    "VN": ("Vietnam", "Vietnamese", []), "ZA": ("South Africa", "South African", []),
    "KE ": ("Kenya", "Kenyan", []),
}
_C2CODE = {}
for _code, (_n, _d, _o) in _COUNTRIES.items():
    _code = _code.strip()
    for _v in [_n, _d, _code] + _o:
        _C2CODE[strip_accents(_v.lower())] = _code
_NAME_VOCAB = sorted(
    {strip_accents(v.lower()): c.strip() for c, (n, d, o) in _COUNTRIES.items()
     for v in [n, d] + [x for x in o if len(x) > 3]}.items(), key=lambda kv: -len(kv[0]))
_NAME_RE = re.compile(r"\b(" + "|".join(re.escape(k) for k, _ in _NAME_VOCAB) + r")\b")


def canon_country(s):
    """Country name / ISO2 code / nationality adjective -> ISO2 (None if unknown)."""
    if s is None:
        return None
    return _C2CODE.get(strip_accents(str(s).strip().lower()))


def countries_in_text(text):
    """Every country (names and nationality words) mentioned in free text -> ISO2 list."""
    t = strip_accents(text.lower())
    seen, out = set(), []
    for m in _NAME_RE.finditer(t):
        c = _C2CODE.get(m.group(1))
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


# --------------------------------------------------------------------------
# Cities
# --------------------------------------------------------------------------
_CITY_ALIASES = [("munich", "munchen", "muenchen"), ("milan", "milano"), ("naples", "napoli"),
                 ("rome", "roma"), ("lisbon", "lisboa"), ("vienna", "wien"),
                 ("cologne", "koln"), ("copenhagen", "kobenhavn"), ("gothenburg", "goteborg")]
_CITY_CANON = {a: g[0] for g in _CITY_ALIASES for a in g}


def city_tokens(s):
    """'Cherry Hill, NJ / Wilmington, DE' -> {'cherry hill', 'wilmington', ...} (accent-folded)."""
    if not s:
        return set()
    out = set()
    for tok in re.split(r"[,/;]", str(s)):
        t = re.sub(r"\s+", " ", strip_accents(tok.lower()).strip())
        if len(t) > 2:
            out.add(_CITY_CANON.get(t, t))
    return out


def city_in(screened_city, city_field, address):
    """Screened city appears in the record's city or address (accent/alias-insensitive)."""
    want = city_tokens(screened_city)
    if not want:
        return True
    have = city_tokens(city_field)
    addr = strip_accents((address or "").lower())
    for w in want:
        if w in have or w in addr:
            return True
        for alias, canon in _CITY_CANON.items():
            if canon == w and (alias in have or alias in addr):
                return True
    return False
