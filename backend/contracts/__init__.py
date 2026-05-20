"""Backend contracts package.

Contracts are TypedDict / type-only definitions.
Zero DB access, no business logic, no side-effects.
Importable without importing the full backend.
"""

__all__ = [
    "analytics_contracts",
    "dashboard_metric_contracts",
    "governance_contracts",
    "integration_contracts",
    "optimization_contracts",
    "publication_contracts",
]
