# DATA MODEL

## Domain Layers

EMS has two main data layers:

- imported data:
  - courses
  - sections
  - enrollments
  - personnel
  - room capacity definitions
- operational data:
  - exam schedules
  - exam rooms
  - invigilator assignments
  - course ownership
  - staff availability blocks
  - workflow session/signatures
  - check-ins
  - QR pickup state
  - exports and print outputs

Imported data provides baseline academic context. Operational data is what the exam office creates and updates on top of it.

## Teaching Room vs Exam Room

### Teaching Room

- Source-side academic room attached to section/course delivery
- Used as a reference
- Helpful when no exam room has been assigned yet

### Exam Room

- Operational room used on exam day
- Has capacity, activity status, and scheduling significance
- May differ from the teaching room
- Used by room attendance, check-ins, exports, and workflow validation

## Course Ownership

- Course ownership is exam-cycle specific
- A section may have different responsible teachers for:
  - midterm
  - final
- Ownership can be imported, auto-assigned, or manually overridden
- Ownership status matters for review readiness and downstream teacher-facing flows

## Staff Workload

Workload is not only invigilation.

Current workload-related concepts include:
- invigilation assignment count
- paper distribution assignment count
- external exam duty count
- historical total workload
- fairness score / balancing context

This means “staff load” should be treated as a composite operational metric, not a single-role metric.

## Staff Availability

- Stored as explicit unavailability blocks
- Can be all-day or time-range specific
- Used before optimization
- Affects invigilator assignment, paper distribution eligibility, and external exam allocation

## QR System

Current QR flow is centered on exam-paper pickup confirmation.

Key ideas:
- QR X:
  - active operational pickup QR
  - can be regenerated
  - regenerated version may require explicit confirmation before activation
- QR Y:
  - remains document/regulation-related
  - not used for pickup confirmation in the current frontend flow

## Exam Lifecycle

Simplified lifecycle:

1. Import academic/source data
2. Review course ownership / teacher responsibility
3. Assign schedules and rooms
4. Optimize invigilators and staff
5. Review issues and start workflow
6. Round 1 sign-off
7. Open swap window if needed
8. Round 2 lock
9. Export documents and operate exam day flows
10. Record attendance/check-ins and print/pickup status

## Workflow Session Model

- Workflow state is session-based
- Session tracks:
  - current status
  - round 1 signatures
  - round 2 signatures
  - baseline saved state
  - next signer per round

This is separate from raw schedule rows. Workflow is a cross-cutting orchestration layer.
