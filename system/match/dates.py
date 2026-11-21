"""Step 1b: dates. Owner: feat/dates.

Planned API (dates are model.PartialDate):
  parse(text) -> PartialDate | None                  ISO, dd/mm/yyyy, '14 March 1988', 'March 14, 1988', yyyy-mm, yyyy
  parse_many(text) -> list[PartialDate]              '1996; 1997'
  birth_years_from_age(age, at: PartialDate) -> list[int]   aged 45 in March 2019 -> [1973, 1974]
  dob_agrees(customer, hit) -> bool                  principle 7
  dob_contradicts(customer, hit_dates) -> bool       principle 6
  age_at(dob, date) -> int | None
"""
