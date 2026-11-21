"""Step 1c: countries. Owner: feat/countries.

Planned API:
  canonical(text) -> str | None                      ISO2 for codes, names, nationalities ('Nigerian' -> 'NG')
  from_address(address) -> str | None                last part of the address
  find_in_text(text) -> list[str]                    countries mentioned in free text
NOT countries: 'International', 'Europe'. Territories are their own country.
"""
