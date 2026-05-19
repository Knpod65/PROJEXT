"""Integration contract registry service.

Registry exposing the five cross-system integration contracts defined in
integration_contracts.py. Pure logic. No DB. No ORM.
"""
from __future__ import annotations

from typing import List, Optional

from contracts.integration_contracts import IntegrationContract, INTEGRATION_CONTRACTS


def list_contracts() -> List[IntegrationContract]:
    """Return a shallow copy of the master contract list."""
    return list(INTEGRATION_CONTRACTS)


def get_contract(system_code: str) -> Optional[IntegrationContract]:
    """Return the contract for *system_code* or None if not found."""
    for contract in INTEGRATION_CONTRACTS:
        if contract["system_code"] == system_code:
            return contract
    return None


def list_inbound_contracts() -> List[IntegrationContract]:
    """Return contracts where integration_direction is 'inbound' or 'bidirectional'."""
    return [c for c in INTEGRATION_CONTRACTS 
            if c["integration_direction"] in ("inbound", "bidirectional")]


def list_outbound_contracts() -> List[IntegrationContract]:
    """Return contracts where integration_direction is 'outbound' or 'bidirectional'."""
    return [c for c in INTEGRATION_CONTRACTS 
            if c["integration_direction"] in ("outbound", "bidirectional")]


def get_contract_pdpa_level(system_code: str) -> Optional[str]:
    """Return the PDPA level string for a system code, or None."""
    contract = get_contract(system_code)
    if contract is None:
        return None
    return contract["pdpa_level"]


def validate_contract_fields(system_code: str, payload: dict) -> bool:
    """Return True if *payload* contains all required fields for *system_code*.

    Missing or extra optional fields are permitted; only required fields
    must be present. Does not validate field values or types.
    """
    contract = get_contract(system_code)
    if contract is None:
        return False
    required = set(contract["required_fields"])
    return required.issubset(payload.keys())
