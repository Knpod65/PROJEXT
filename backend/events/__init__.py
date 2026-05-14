"""Domain event package for EMS.

Re-exports the make_domain_event factory for convenient importing.
"""
from events.domain_event import DomainEvent, make_domain_event

__all__ = ["DomainEvent", "make_domain_event"]
