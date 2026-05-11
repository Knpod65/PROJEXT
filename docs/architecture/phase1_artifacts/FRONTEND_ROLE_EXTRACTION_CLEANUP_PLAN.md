# Frontend Role Extraction Cleanup Plan
## Phase 1 Artifact — Eliminating DRY Violations in Role Access Logic

**Purpose:** Document the inefficient copy-paste pattern of role extraction logic across frontend pages, and specify the safe migration path to centralized semantic permission checking.

**Source of Truth:**
- docs/architecture/UI_SYSTEM_AND_ROLE_THEME_GUIDE.md (§3 "The Role Extraction Problem")
- Code audit: Checkins.tsx:77, Schedule.tsx:21, ExportCenter.tsx:51
- Existing utility: frontend/src/utils/roles.ts exports getEffectiveRole(user)

---

## 1. Current Problem Analysis

### Pattern: Copy-Paste Null-Coalescing Chain

The same three-level fallback chain is repeated verbatim in multiple page components:

```typescript
// Instance 1: frontend/src/pages/Checkins.tsx:77
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;

// Instance 2: frontend/src/pages/Schedule.tsx:21
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;

// Instance 3: frontend/src/pages/ExportCenter.tsx:51
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;
```

### Issues

1. **DRY Violation:** Three identical implementations mean three places to update if resolution logic changes
2. **Maintenance Risk:** Drift risk — each copy could diverge (e.g., one reverses operator precedence, one skips a fallback)
3. **Incomplete Logic:** This manual chain does NOT handle admin impersonation (`user.view_as_role`), but the canonical `getEffectiveRole()` in utils/roles.ts does
4. **Hidden Dependencies:** No clear indication that this logic is role resolution; readers must infer intent from the chain

### Scope of Pattern

- **Confirmed:** Checkins.tsx:77, Schedule.tsx:21, ExportCenter.tsx:51
- **Likely:** Dashboard.tsx, Submissions.tsx, Optimizer.tsx, and any other page components accessing user.role
- **Estimate:** 6–10 additional instances discovered during Phase 1 audit grep

---

## 2. Current Authorization Architecture

### Route-Level Guards (App.tsx)

Route access is gated in `App.tsx` using `GuardedPage` component:

```typescript
<Route path="/checkins" element={
  <GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}>
    <CheckinsPage />
  </GuardedPage>
} />
```

**Purpose:** Answers "Can this role see this page at all?"
**Current State:** Centralized in App.tsx route definitions; no duplication here ✅

### Page-Level Role Checks (Pages)

Inside page components, inline role checks answer "Can this role perform this specific action?":

```typescript
// Current pattern (WRONG per our policy)
const canManagePickup = effectiveRole === "admin" || effectiveRole === "staff";

// Current pattern (inline permission array, creates drift)
const isApprover = ["admin", "esq_head", "secretary"].includes(effectiveRole);
```

**Problem:** 
- Scattered across pages with no single source of truth
- Product team can't easily change "who can do X" without finding all instances
- Inline role arrays duplicate route-level role information

---

## 3. Target Architecture

### Canonical Role Extraction Function

**Already exists in `frontend/src/utils/roles.ts`:**

```typescript
export function getEffectiveRole(user: User | null): UserRole | null {
  if (!user) return null;
  return user.effective_role ?? user.active_role ?? user.role ?? null;
}
```

**Advantages:**
- Single source of truth for role extraction logic
- Handles admin impersonation correctly (assumes effective_role is pre-computed by auth context)
- Testable as a pure function
- Clear intent via function name

### Recommended Hook Wrapper

**Create `frontend/src/hooks/useEffectiveRole.ts`:**

```typescript
import { getEffectiveRole } from "@/utils/roles";
import { useAuth } from "@/store/auth.store";
import type { UserRole } from "@/types/api";

export function useEffectiveRole(): UserRole | null {
  const { user } = useAuth();
  return getEffectiveRole(user);
}
```

**Usage in pages:**
```typescript
const effectiveRole = useEffectiveRole();  // ← Clear, single source
```

### Semantic Permission Checking

**Create `frontend/src/hooks/usePermission.ts`:**

```typescript
import { useEffectiveRole } from "./useEffectiveRole";
import type { UserRole } from "@/types/api";

const PERMISSION_MAP: Record<string, UserRole[]> = {
  "manage_pickup": ["admin", "staff"],
  "manage_swaps": ["admin", "staff", "teacher"],
  "approve_submission": ["admin"],
  // ... 15+ semantic actions
};

export function usePermission(action: string): boolean {
  const role = useEffectiveRole();
  if (!role) return false;
  const allowed = PERMISSION_MAP[action];
  return allowed?.includes(role) ?? false;
}
```

**Usage in pages:**
```typescript
const canManagePickup = usePermission("manage_pickup");  // ← Semantic, single source
```

---

## 4. Migration Path (Safe, Low-Risk)

### Phase 1 — Quick Win #2 (1–2 hours)

**Scope:** Replace confirmed 3 role extraction instances

1. Replace Checkins.tsx:77
   ```typescript
   // BEFORE
   const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;
   
   // AFTER
   const effectiveRole = useEffectiveRole();
   ```

2. Replace Schedule.tsx:21 (identical change)

3. Replace ExportCenter.tsx:51 (identical change)

4. Create ESLint rule or grep check to block future patterns:
   ```bash
   # CI check: fail if pattern found in frontend/src/pages/*.tsx
   grep -r "effective_role ?? .*active_role" frontend/src/pages/
   ```

5. Commit: minimal, low-risk, zero behavior change

### Phase 2 — Permission Hook Foundation (1 week)

**Scope:** Create permission hook and populate PERMISSION_MAP for all semantic actions

1. Create `frontend/src/hooks/usePermission.ts` with PERMISSION_MAP
2. Update Checkins.tsx to use `usePermission("manage_pickup")` where applicable
3. Update other pages similarly
4. Update tests to verify PERMISSION_MAP coverage

### Phase 3+ — Full Semantic Conversion

Once usePermission is stable, gradually convert all inline role checks:

```typescript
// BEFORE (scattered, risky)
const canApprove = ["admin", "esq_head", "secretary"].includes(effectiveRole);
const canSubmit = effectiveRole === "teacher";
const canViewAudit = effectiveRole === "admin";

// AFTER (centralized, semantic)
const canApprove = usePermission("approve_submission");
const canSubmit = usePermission("submit_exam");
const canViewAudit = usePermission("view_audit_logs");
```

---

## 5. Affected Files Inventory

### Files with Confirmed Role Extraction Issues

| File | Line(s) | Pattern | Priority |
|------|---------|---------|----------|
| Checkins.tsx | 77 | `?.effective_role ?? ?.active_role ?? ?.role ?? null` | HIGH (QW #2) |
| Schedule.tsx | 21 | Same | HIGH (QW #2) |
| ExportCenter.tsx | 51 | Same | HIGH (QW #2) |

### Files Likely to Have Role Checks (Audit Required)

| File | Likely Issues | Estimate |
|------|---------------|----------|
| Dashboard.tsx | Inline role arrays, page-level guards | 2–3 instances |
| Submissions.tsx | Page-level role gates, teacher ownership | 3–4 instances |
| Optimizer.tsx | Admin-only checks, signing role checks | 2–3 instances |
| WorkflowV2.tsx | Signer role validation | 1–2 instances |
| ExamManager.tsx | Ownership and role checks | 1–2 instances |
| Period.tsx | Admin-only operations | 1–2 instances |

**Total estimated instances:** 13–19 beyond the confirmed 3

### No Issues Expected

| File | Reason |
|------|--------|
| App.tsx | Route guards are centralized in GuardedPage ✅ |
| ImportV2.tsx | Admin-only route, no page-level role variance |
| UsersV2.tsx | Admin-only route |

---

## 6. Regression Testing Strategy

### Unit Tests (Per Hook)

```typescript
// tests/hooks/useEffectiveRole.test.ts
describe('useEffectiveRole', () => {
  it('returns effective_role if present', () => {
    const user = { effective_role: 'admin', active_role: 'staff', role: 'teacher' };
    expect(getEffectiveRole(user)).toBe('admin');
  });
  
  it('falls back to active_role if effective_role is absent', () => {
    const user = { active_role: 'staff', role: 'teacher' };
    expect(getEffectiveRole(user)).toBe('staff');
  });
  
  it('falls back to role as final fallback', () => {
    const user = { role: 'teacher' };
    expect(getEffectiveRole(user)).toBe('teacher');
  });
  
  it('returns null if user is null', () => {
    expect(getEffectiveRole(null)).toBeNull();
  });
});
```

### Integration Test (Permission Map)

```typescript
// tests/hooks/usePermission.test.ts
describe('usePermission', () => {
  it('allows admin for manage_pickup', () => {
    // Arrange: mock useEffectiveRole to return 'admin'
    jest.mock('./useEffectiveRole', () => ({ useEffectiveRole: () => 'admin' }));
    // Act
    const result = usePermission('manage_pickup');
    // Assert
    expect(result).toBe(true);
  });
  
  it('denies teacher for manage_pickup', () => {
    // Similar test structure
    expect(result).toBe(false);
  });
});
```

### Page-Level Regression Test

For each affected page, verify permission checks still render/hide UI correctly:

```typescript
// tests/pages/Checkins.test.tsx
test('Pickup button hidden for teacher role', () => {
  render(<CheckinsPage />, { 
    user: { role: 'teacher', effective_role: 'teacher' } 
  });
  expect(screen.queryByText('Manage Pickup')).not.toBeInTheDocument();
});

test('Pickup button visible for admin role', () => {
  render(<CheckinsPage />, { 
    user: { role: 'admin', effective_role: 'admin' } 
  });
  expect(screen.getByText('Manage Pickup')).toBeInTheDocument();
});
```

### Behavior Equivalence Verification

Before and after each migration, verify no UI changes:

```bash
# Visual regression test: capture screenshot before change
npm run test:visual:capture -- Checkins

# Make change

# Compare screenshot after change
npm run test:visual:compare -- Checkins
# Should pass with 0 pixel differences
```

---

## 7. Implementation Checklist

### Phase 1 (Quick Win #2) — 1–2 hours
- [ ] Verify `frontend/src/utils/roles.ts` exports `getEffectiveRole(user)`
- [ ] Create `frontend/src/hooks/useEffectiveRole.ts` with hook wrapper
- [ ] Replace Checkins.tsx:77 with `useEffectiveRole()`
- [ ] Replace Schedule.tsx:21 with `useEffectiveRole()`
- [ ] Replace ExportCenter.tsx:51 with `useEffectiveRole()`
- [ ] Write unit tests for useEffectiveRole hook
- [ ] Add ESLint rule or CI grep check to prevent pattern reintroduction
- [ ] Commit PR with change summary
- [ ] Manual QA: Verify Checkins, Schedule, ExportCenter pages still work for each role

### Phase 2 (Permission Hook) — 1 week
- [ ] Create `frontend/src/hooks/usePermission.ts` with PERMISSION_MAP
- [ ] Document all semantic actions in PERMISSION_MAP (15+ actions)
- [ ] Write permission map tests
- [ ] Identify all 13–19 additional role check instances via grep
- [ ] Begin converting page-level checks to usePermission() calls
- [ ] Update tests for each converted page
- [ ] Update CI to verify usePermission() coverage

---

## 8. Risk Assessment

### Low Risk (Quick Win #2)
- **Change:** Replace manual chain with existing function
- **Scope:** 3 locations only
- **Behavior:** Identical (manual chain already calls getEffectiveRole logic implicitly)
- **Testing:** Hook unit tests + page regression tests
- **Rollback:** Simple revert to inline chains if needed

### Medium Risk (Permission Map)
- **Change:** Centralize role-based business rules
- **Scope:** 13–19 page locations
- **Behavior:** Should be identical, but drift risk if PERMISSION_MAP is incomplete
- **Testing:** Comprehensive permission map tests + page-level QA
- **Mitigation:** Iterative rollout (one page at a time), feature flags if needed

### Known Issues (NOT in scope for this plan)
- Admin impersonation (`view_as_role`) is assumed to be pre-computed in user context — not changing
- Role theme colors are separate from role extraction — not in scope
- Route guards in App.tsx are already centralized — not changing

---

## 9. Success Criteria

✅ **Phase 1 QW #2 Complete:**
- 3 role extraction chains replaced with useEffectiveRole()
- ESLint/CI check prevents pattern reintroduction
- No UI regression in affected pages
- Unit tests pass for hook

✅ **Phase 2 Permission Hook Complete:**
- usePermission hook exists with 15+ semantic actions
- 13–19 page-level role checks converted to usePermission()
- PERMISSION_MAP has >95% coverage of product-defined actions
- All converted pages pass regression tests

✅ **Overall Goal:**
- Zero instances of manual `?.effective_role ?? ?.active_role ?? ?.role` chains in frontend/src/pages/
- All role checking uses semantic hooks (useEffectiveRole or usePermission)
- Single source of truth for role resolution and permission mapping
