# Governance Flow Configuration

**Phase:** D3.3
**Model:** `backend/config_models/governance_flow.py`
**Service:** `backend/services/governance_flow_service.py`

---

## Overview

`GovernanceFlowConfig` is a configurable replacement for the hardcoded
`settings.sign_order_usernames` signer chain. It supports multi-round
approval with per-slot role requirements and quorum control.

`settings.sign_order_usernames` is **NOT modified** — `build_default_flow_from_settings()`
reads it on demand and caches the result as the global default flow.

---

## Data Model

```python
@dataclass(frozen=True)
class SignerSlot:
    position: int             # 1-based slot index
    role: str                 # expected role for this slot
    username_hint: str | None # optional specific username
    required: bool            # must sign before advancing

@dataclass(frozen=True)
class GovernanceFlowConfig:
    faculty_id: int | None    # None = global/default flow
    flow_name: str
    round_1_signers: tuple[SignerSlot, ...]
    round_2_signers: tuple[SignerSlot, ...]
    requires_governance_review: bool
    approval_quorum: int      # minimum required signers per round
    created_at: str           # UTC ISO
    metadata: dict[str, Any]
```

---

## Resolution Chain

```
get_effective_flow(faculty_id=F)

1. Faculty-specific flow registered for F      → return it
2. Global flow registered (faculty_id=None)    → return it
3. No global registered                        → auto-build from settings.sign_order_usernames
```

---

## Backward Compatibility Shim

```python
get_signer_order(faculty_id=None) -> tuple[str | None, ...]
# Returns username_hints from round_1_signers — drop-in for code using
# settings.sign_order_usernames directly.
```

---

## Validation Rules

| Severity | Rule |
|---|---|
| HARD_FAIL | No round_1_signers |
| HARD_FAIL | approval_quorum > len(round_1_signers) |
| HARD_FAIL | Empty flow_name |
| WARNING   | round_2_signers is empty |
| INFO      | requires_governance_review = False |

---

## Example: Register Faculty-Specific Flow

```python
from config_models.governance_flow import make_governance_flow_config
from services.governance_flow_service import register_governance_flow

flow = make_governance_flow_config(
    "eng_approval",
    round_1_signers=[
        {"position": 1, "role": "esq_head", "username_hint": "dean.eng", "required": True},
    ],
    round_2_signers=[
        {"position": 1, "role": "admin", "username_hint": None, "required": False},
    ],
    faculty_id=2,
    requires_governance_review=True,
    approval_quorum=1,
)
register_governance_flow(flow)
```
