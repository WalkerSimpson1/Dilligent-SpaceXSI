"""Contract objects used by Step 2. Reconcile with Step 0's model.py when it lands:
keep the field names, add what is missing."""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Fact:
    value: object            # the fact (string, ISO2 code, partial-date tuple, ...)
    source_id: str           # ID of the record that supports it (CUS-, KYC-, NOTE-, ...)
    kind: str                # e.g. 'full_name', 'crm_dob', 'verified_dob', 'residence', 'lived'
    when: Optional[str] = None   # ISO date of the source, when relevant


@dataclass
class Verified:
    """Most recent APPROVED identity check of the person (KYC provider or onboarding note)."""
    source_id: str           # KYC-... or NOTE-...
    name: Optional[str]
    dob: Optional[Tuple]     # partial date (y, m, d)
    doc_country: Optional[str]   # ISO2
    when: Optional[str]      # ISO date used for 'most recent'
    doc_number: Optional[str] = None


@dataclass
class CustomerPicture:
    """One real-world person (possibly several CRM records)."""
    person_key: str                          # smallest record id in the cluster
    record_ids: List[str]
    entity_type: str                         # Individual | Company
    names: List[Fact] = field(default_factory=list)       # full / preferred / login names
    verified: Optional[Verified] = None
    dobs: List[Fact] = field(default_factory=list)        # CRM dobs + verified dob (kind tells which)
    countries: List[Fact] = field(default_factory=list)   # residence / nationality / document / lived
    cities: List[Fact] = field(default_factory=list)
    evidence_ids: List[str] = field(default_factory=list)  # every record the facts came from


@dataclass
class Resolution:
    alert_id: str
    link: str                                # account | login | email | search | none
    pictures: List[CustomerPicture]          # distinct persons that fit; >1 => step 4 decides each
    note: str = ""                           # e.g. 'no_candidates', 'joint_holders_filtered'

    @property
    def ambiguous(self):
        return len(self.pictures) > 1

    def customer_record_id(self):
        """Value for the output field, before step 4 decides per person."""
        if not self.pictures:
            return None
        if len(self.pictures) > 1:
            return "AMBIGUOUS"
        return self.pictures[0].record_ids[0]
