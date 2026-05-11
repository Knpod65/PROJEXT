# UI System and Role Theme Guide
## EMS — RBAC-UI Integration Layer

> **Audience:** Frontend engineers
> **Scope:** Role-theme wiring, permission hook design, role extraction patterns, form validation, skeleton loading standardization, error handling hierarchy
> **EXTENDS** `docs/UI_SYSTEM.md` — this document covers ONLY the RBAC-UI integration layer
> **Do NOT duplicate** component design rules from `docs/UI_SYSTEM.md`
> **Reference files:** `frontend/src/theme/roleThemes.ts`, `frontend/src/utils/roles.ts`, `frontend/src/store/auth.store.tsx`, `frontend/src/App.tsx`, `frontend/src/pages/Checkins.tsx`

---

## 1. What This Extends

`docs/UI_SYSTEM.md` covers layout rules, table conventions, scrolling, empty/loading states,
typography, and i18n patterns. Read that document first.

This document covers **how roles flow through the UI system**:
- How the role theme is wired from `roleThemes.ts` to CSS variables
- The role extraction problem and its canonical fix
- The `usePermission(action)` hook design
- When and where role gates belong
- Form validation before API calls
- Skeleton loading standardization
- Error handling hierarchy

---

## 2. Role Theme Wiring

### Data Flow

```
roleThemes.ts                           AppShell.tsx
─────────────────────────────────────   ─────────────────────────
const roleThemes = {                    // getRoleThemeStyle() returns inline styles:
  admin: {                              // {
    accent: "#1f4d8f",                  //   "--role-accent": "#1f4d8f",
    sidebarBg: "#1a3a6b",               //   "--role-sidebar-bg": "#1a3a6b",
    accentText: "#fff",                 //   "--role-accent-text": "#fff",
    ...17 more fields                   //   ... etc.
  },                                    // }
  esq_head: { ... },                    style={getRoleThemeStyle(theme)}
  ...8 roles total                      // Applied to the AppShell root element
}
```

### The 10 CSS Custom Properties

| Variable | Usage |
|----------|-------|
| `--role-accent` | Primary action buttons, active nav item |
| `--role-accent-strong` | Hover state on accent elements |
| `--role-accent-text` | Text color on accent-background elements |
| `--role-accent-soft` | Light tint for backgrounds, badges |
| `--role-sidebar-bg` | Sidebar/navigation background |
| `--role-sidebar-text` | Sidebar text and icon color |
| `--role-sidebar-active` | Active nav item background |
| `--role-badge-bg` | Role chip/badge background |
| `--role-badge-text` | Role chip/badge text |
| `--role-border` | Accent-colored borders |

### Where to Consume Theme Variables

Use CSS custom properties in component stylesheets, not hardcoded hex values:
```css
/* CORRECT */
.action-button { background: var(--role-accent); color: var(--role-accent-text); }
.sidebar-item.active { background: var(--role-sidebar-active); }

/* WRONG — hardcoded colors bypass the role theme system */
.action-button { background: #1f4d8f; }
```

### Current Gap

Theme variables are applied via **inline styles** on the AppShell root element. This is
functional but has a side effect: if any child component also uses inline styles, specificity
conflicts can occur. Phase 4 improvement: switch to `data-role="admin"` attribute on the
HTML body, with CSS rules scoped to `[data-role="admin"] .action-button { ... }`.

---

## 3. The Role Extraction Problem

### The Bug (confirmed in 3 locations)

The same null-coalescing chain is copy-pasted verbatim across multiple page components:

```typescript
// frontend/src/pages/Checkins.tsx:77
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;

// frontend/src/pages/Schedule.tsx:21
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;

// frontend/src/pages/ExportCenter.tsx:51
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;
```

This pattern has three problems:
1. **DRY violation** — when the resolution logic needs to change, all 3 (and possibly more undiscovered) locations must be updated
2. **Subtle inconsistency** — each copy could drift to a slightly different chain order
3. **Misses admin impersonation** — the canonical `getEffectiveRole()` function in `utils/roles.ts` handles the `view_as_role` case correctly; this manual chain may not

### The Fix (already exists)

`frontend/src/utils/roles.ts` already exports `getEffectiveRole(user)`:
```typescript
// Already implemented — use this
export function getEffectiveRole(user: User | null): UserRole | null {
  if (!user) return null;
  return user.effective_role ?? user.active_role ?? user.role ?? null;
}
```

**Replace all 3 (and any future) occurrences:**
```typescript
// BEFORE (in each page)
const effectiveRole = user?.effective_role ?? user?.active_role ?? user?.role ?? null;

// AFTER
import { getEffectiveRole } from "@/utils/roles";
const effectiveRole = getEffectiveRole(user);
```

**Phase 1 quick win:** Create a CI lint rule (ESLint custom rule or grep check) that blocks
any new code that uses `?.effective_role ?? ?.active_role` — force use of `getEffectiveRole()`.

### Recommended Wrapper Hook

For convenience in components:
```typescript
// frontend/src/hooks/useEffectiveRole.ts
import { getEffectiveRole } from "@/utils/roles";
import { useAuth } from "@/store/auth.store";
import type { UserRole } from "@/types/api";

export function useEffectiveRole(): UserRole | null {
  const { user } = useAuth();
  return getEffectiveRole(user);
}
```

---

## 4. `usePermission(action)` Hook Design

### Problem: Scattered Role Checks in Pages

Currently, role checks in pages are expressed as inline arrays:
```typescript
// frontend/src/pages/Checkins.tsx:78
const canManagePickup = effectiveRole === "admin" || effectiveRole === "staff";
```

This pattern has no single source of truth for "who can do X." If the product team changes
the rule, every file must be found and updated.

### Solution: Semantic Permission Hook

```typescript
// frontend/src/hooks/usePermission.ts

import { useEffectiveRole } from "./useEffectiveRole";
import type { UserRole } from "@/types/api";

const PERMISSION_MAP: Record<string, UserRole[]> = {
  // Staff Operations
  "manage_pickup":        ["admin", "staff"],
  "manage_swaps":         ["admin", "staff", "teacher"],
  "view_checkins":        ["admin", "dept_supervisor", "staff", "teacher"],
  "manage_checkins":      ["admin", "staff"],
  // Submission & Approval
  "submit_exam":          ["teacher"],
  "approve_submission":   ["admin"],
  "view_submissions":     ["admin", "esq_head", "secretary", "dept_supervisor", "teacher"],
  // Export Center
  "export_schedule":      ["admin", "staff"],
  "export_workload":      ["admin", "staff"],
  "export_compensation":  ["admin"],
  // Administration
  "manage_users":         ["admin"],
  "manage_periods":       ["admin"],
  "run_optimizer":        ["admin"],
  "view_audit_logs":      ["admin"],
  "sign_workflow":        ["admin", "esq_head", "secretary"],
  // Print
  "manage_print_queue":   ["print_shop"],
  "view_print_review":    ["admin", "esq_head", "secretary"],
};

export function usePermission(action: string): boolean {
  const role = useEffectiveRole();
  if (!role) return false;
  const allowed = PERMISSION_MAP[action];
  if (!allowed) {
    if (process.env.NODE_ENV === "development") {
      console.warn(`usePermission: unknown action "${action}"`);
    }
    return false;
  }
  return allowed.includes(role);
}
```

**Usage in pages:**
```typescript
// BEFORE
const canManagePickup = effectiveRole === "admin" || effectiveRole === "staff";

// AFTER
const canManagePickup = usePermission("manage_pickup");
```

---

## 5. `GuardedPage` vs Page-Level Role Checks

### The Policy

**Route guards belong in `App.tsx` only.** Pages must not re-check roles via inline arrays.

```typescript
// frontend/src/App.tsx — CORRECT: role arrays live here, in route declarations
<Route path="/checkins" element={
  <GuardedPage roles={["admin", "dept_supervisor", "staff", "teacher"]}>
    <CheckinsPage />
  </GuardedPage>
} />

// frontend/src/pages/Checkins.tsx — CORRECT: use semantic permission hook for feature-level checks
const canManagePickup = usePermission("manage_pickup");
```

```typescript
// frontend/src/pages/Checkins.tsx — WRONG: duplicates route-level guard
if (effectiveRole !== "admin" && effectiveRole !== "staff" && effectiveRole !== "teacher") {
  return <UnauthorizedPage />;
}
```

### Rule
- `GuardedPage` (in `App.tsx`): "Can this role see this page at all?"
- `usePermission(action)` (in pages): "Can this role perform this specific action within the page?"
- Never use `roles={[...]}` prop syntax outside of `App.tsx` route declarations

---

## 6. Form Validation Pattern

### Current Gap

Forms currently coerce types at submission time, silently producing `NaN` or empty values:
```typescript
// frontend/src/pages/Checkins.tsx:182 — current pattern (risky)
students_present: studentsPresent ? Number(studentsPresent) : undefined,
// Problem: Number("abc") === NaN — no error is thrown; NaN reaches the API
```

### Required Pattern: Validate Before API Call

For all mutation forms, validate input before calling the service:

```typescript
// Validation function (can use Zod or manual checks)
function validateCheckinInput(data: {
  studentsPresent: string;
  lateCount: string;
}): { students_present: number; late_count: number } {
  const students = parseInt(data.studentsPresent, 10);
  if (isNaN(students) || students < 0 || students > 9999) {
    throw new Error(t("checkins.validation.invalidStudentCount"));
  }
  const late = data.lateCount ? parseInt(data.lateCount, 10) : 0;
  if (isNaN(late) || late < 0 || late > students) {
    throw new Error(t("checkins.validation.invalidLateCount"));
  }
  return { students_present: students, late_count: late };
}

// Usage in submit handler
const handleCreateCheckin = async (event: React.FormEvent) => {
  event.preventDefault();
  try {
    const validated = validateCheckinInput({ studentsPresent, lateCount });
    await createCheckin({ ...validated, schedule_id: selectedSchedule.id });
  } catch (err) {
    toast(err instanceof Error ? err.message : t("errors.generic"), "error");
  }
};
```

### Zod Schemas (Phase 4 target)

For complex forms, centralize schema in `frontend/src/schemas/`:
```typescript
// frontend/src/schemas/checkin.schema.ts
import { z } from "zod";

export const CreateCheckinSchema = z.object({
  schedule_id: z.number().int().positive(),
  students_present: z.number().int().min(0).max(9999),
  late_count: z.number().int().min(0).optional(),
  notes: z.string().max(500).optional(),
});

export type CreateCheckinInput = z.infer<typeof CreateCheckinSchema>;
```

---

## 7. Skeleton Loading Standardization

### Current Duplication (6+ copy-paste instances)

The same skeleton pattern appears verbatim across multiple pages:
```typescript
// Checkins.tsx:362-366, Schedule.tsx:191-195 — identical code
{Array.from({ length: 3 }).map((_, index) => (
  <Skeleton key={index} className="card-skeleton" />
))}
```

### Standardized Component

Create a single `<PageSkeleton>` component:
```typescript
// frontend/src/components/ui/PageSkeleton.tsx
interface PageSkeletonProps {
  variant: "table" | "cards" | "form";
  count?: number;
}

export function PageSkeleton({ variant, count = 3 }: PageSkeletonProps) {
  if (variant === "table") {
    return (
      <div className="skeleton-table">
        {Array.from({ length: count }).map((_, i) => (
          <Skeleton key={i} className="skeleton-row" />
        ))}
      </div>
    );
  }
  if (variant === "cards") {
    return (
      <section className="operations-summary-grid">
        {Array.from({ length: count }).map((_, i) => (
          <Skeleton key={i} className="card-skeleton" />
        ))}
      </section>
    );
  }
  if (variant === "form") {
    return (
      <div className="skeleton-form">
        {Array.from({ length: count }).map((_, i) => (
          <Skeleton key={i} className="skeleton-field" />
        ))}
      </div>
    );
  }
}
```

**Migration:** Replace all `{Array.from({ length: N }).map(...)}` skeleton patterns with
`<PageSkeleton variant="cards" count={N} />`.

---

## 8. Error Handling Hierarchy

Three tiers of error handling, each with a specific use case. They must not be mixed.

### Tier 1: Toast (transient, user-facing, non-blocking)
**When:** API call fails, async operation error, network error
**How:** `toast(message, "error")` from `UiProvider`
```typescript
try {
  await confirmSwap(swapId);
} catch (err) {
  toast(err instanceof Error ? err.message : t("swaps.toast.confirmFailed"), "error");
}
```

### Tier 2: Inline Error (field-level, blocking, persistent)
**When:** Form validation failure, field-specific error from API (422 validation error)
**How:** Error message rendered near the field
```typescript
const [fieldError, setFieldError] = useState<string | null>(null);
// ... in submit handler:
setFieldError(t("checkins.validation.invalidStudentCount"));
// ... in JSX:
{fieldError && <p className="field-error">{fieldError}</p>}
```

### Tier 3: Error Boundary (render crash, full-component fallback)
**When:** Unexpected runtime error in render (not async)
**How:** `ErrorBoundary` component already wraps `<Outlet />` in `ProtectedAppLayout`
**Never catch in:** render functions, `useEffect` cleanup (let ErrorBoundary handle it)

### The `useAsyncData` Hardcoded Thai String (Must Fix)
**File:** `frontend/src/hooks/useAsyncData.ts` line 25
**Current:** `setError("เกิดข้อผิดพลาด")` — hardcoded Thai string
**Fix:** Since `useAsyncData` is not a React component, it cannot use the `useI18n()` hook directly.

Option A — Pass the error formatter as a parameter:
```typescript
export function useAsyncData<T>(
  loader: () => Promise<T>,
  deps: unknown[],
  options?: { errorMessage?: string }
) {
  ...
  } catch (err) {
    setError(options?.errorMessage ?? "An error occurred");
  }
```

Option B — Import the i18n translate function directly (not the hook):
```typescript
import { translate } from "@/i18n";
// ...
setError(err instanceof Error ? err.message : translate("errors.generic"));
```

Option A is preferred — it keeps `useAsyncData` generic and caller-controlled.
