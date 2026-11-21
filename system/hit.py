"""Step 3: hit profile. Owner: feat/hit.

Contract: profile(hit, data) -> HitPicture
"""
from __future__ import annotations

from data import Data, as_list
from model import Fact, HitPicture


def profile(hit: dict, data: Data) -> HitPicture:
    category = hit.get("primary_category") or (as_list(hit.get("categories")) or ["Other"])[0]
    pic = HitPicture(
        hit_id=hit["hit_id"],
        alert_id=hit["alert_id"],
        entity_type=hit.get("entity_type") or "",
        primary_category=category,
    )
    for n in [hit.get("name"), *as_list(hit.get("aliases"))]:
        if n:
            pic.names.append(Fact("name", n, hit["hit_id"]))
    # TODO 3.1 dobs, deceased_date, countries/nationality/citizenship/addresses/place_of_birth
    # TODO 3.2 DOB from the first paragraph of profile_notes (explicit date or age at a date)
    # TODO 3.3 dated reports: "According to ...; September 10, 2025: ..."
    # TODO 3.4 search results (listing phrase + tied country) when no DOB found
    return pic
