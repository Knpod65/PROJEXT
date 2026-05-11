# EMS Service Layer — Phase 3 foundation
# Plain Python; no FastAPI imports, no Depends(), no HTTPException here.
# Routers call services; services raise EMSDomainError subclasses which
# routers translate to HTTPException.
