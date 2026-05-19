"""User serializer (example).

PDPA-aware: avoid returning sensitive fields unless explicit consent is present.
Serializers should be used by routers/services to shape responses.
"""
from typing import Dict, Any


def serialize_user(user: Dict[str, Any]) -> Dict[str, Any]:
    """Return a safe representation of a user.

    Expected input is a mapping (ORM row or dict). This function is intentionally
    simple and pure — do not perform DB or auth operations here.
    """
    # PDPA-safe: hide email if the record indicates no consent
    pdpa_consent = user.get("pdpa_consent") or user.get("consent")

    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "name": user.get("full_name") or user.get("name"),
        "role": user.get("role"),
        # email only returned when PDPA consent is present
        "email": user.get("email") if pdpa_consent else None,
    }
