"""Backend serializers package.

This package will contain pure serializer/transformer functions and classes
that convert domain models or ORM rows into API-safe dictionaries.
Serializers must be pure (no DB access, no auth checks, no side-effects).
"""

__all__ = [
    "user_serializer",
]
