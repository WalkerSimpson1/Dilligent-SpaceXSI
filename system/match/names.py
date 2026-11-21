"""Step 1a: name matching (POLICY principle 8). Owner: feat/names.

Planned API:
  parts(name, is_company, variants) -> list[str]     normalised, deduped real parts
  parts_match(a, b, variants) -> bool                identical / variant / joined / edit distance
  names_agree(a, b, variants) -> (bool, matched_parts)
  is_undecidable(name) -> bool                       fewer than 2 real parts
"""
