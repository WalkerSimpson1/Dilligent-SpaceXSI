"""Step 2: customer resolution. Owner: feat/customer.

Contract: resolve(alert, data) -> list[CustomerPicture]
  - []            no customer record found      -> customer_record_id null
  - [one]         one person (possibly several merged records, principle 3)
  - [two or more] several distinct people fit   -> step 4 decides per person
"""
from __future__ import annotations

from data import Data
from model import CustomerPicture


def resolve(alert: dict, data: Data) -> list[CustomerPicture]:
    # TODO 2.1 follow account_ref / login_handle / email links (joint holders!)
    # TODO 2.2 search the CRM when the alert has no link
    # TODO 2.3 merge records: same phone + same full DOB, or same approved KYC document number
    # TODO 2.4 verified identity: most recent approved KYC check or KYC note
    # TODO 2.5 countries and cities from notes
    return []
