# WORKFLOW

## Purpose

The workflow module controls readiness review and institutional sign-off before exam operations are treated as finalized.

## Main Flow

### Step 1: Admin prepares data

- import source data
- review ownership
- assign rooms
- run optimizer
- resolve blocking issues

### Step 2: Workflow session starts

- admin initializes the workflow session
- session enters round 1 signing
- issue review checkpoint becomes the main readiness surface

### Step 3: Round 1 sign-off

- intended as pre-swap confirmation
- governance roles review readiness and sign
- once round 1 is complete, the schedule is stable enough to open swap handling

### Step 4: Swap window

- swap window is opened after round 1 completes
- swap/change requests can be handled during this stage
- this stage exists before final lock to allow controlled operational change

### Step 5: Round 2 sign-off

- post-swap locking round
- final signers confirm the post-adjustment state
- after completion, the schedule is treated as locked for downstream operations

## Admin -> ESQ -> Secretary Perspective

- `admin`:
  - prepares data
  - initializes session
  - can open swap window
  - participates in sign-off where applicable
- `esq_head`:
  - governance review
  - signs during workflow rounds
- `secretary`:
  - governance review and signature participation

The frontend currently models governance participation as a shared sign-off lane for `admin`, `esq_head`, and `secretary`.

## Approval / Rejection Reality

Current UI is centered on:
- issue visibility
- readiness validation
- signature progression

There is no separate rich rejection UI in the current V2 workflow page. The practical equivalent of “reject” today is:
- do not advance
- resolve issues
- rerun optimizer or adjust underlying data
- then continue signing

## Reset / Rework Logic

When readiness is not acceptable, the team should treat workflow as a checkpoint and go back to:
- schedule correction
- room correction
- staffing correction
- external exam allocation correction
- availability correction

The session should not advance until blockers are removed.

## Swap Window

- sits between round 1 and round 2
- exists to handle operational changes after an initial approved baseline
- final lock should happen only after swap-related adjustments are settled

## Optimization Relationship

Workflow depends on optimizer output.

Typical dependency chain:
- optimizer generates room/invigilator allocations
- workflow validates issues against those allocations
- workflow sign-off makes that state institutionally ready

If optimizer output changes materially, workflow review should be revisited.
