"""Tiny sample money-path module, used to trigger the 'money-path' rules."""
from decimal import Decimal


def add_charge(ledger: dict, event_id: str, tenant_id: str, amount: Decimal) -> bool:
    """Append a charge once per event_id. Returns False if it was a duplicate."""
    if event_id in ledger:
        return False
    ledger[event_id] = {"tenant_id": tenant_id, "amount": amount}
    return True
# billing tweak
