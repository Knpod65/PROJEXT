# Developer Workflow Guide

## Repository Setup

### Important: Always open VS Code at the project folder only

**Correct:**
```bash
code /Users/kinompungpound/Downloads/PROJEXT/opt/ems_system
```

**Do NOT open these parent folders** (they should not be Git repositories):
- `/Users/kinompungpound` (home folder)
- `/Users/kinompungpound/Downloads/PROJEXT`

If you accidentally opened a parent folder, close that VS Code window and open the project folder directly. The `.vscode/settings.json` file in this project includes a safety setting (`git.openRepositoryInParentFolders: never`) to prevent VS Code from scanning parent folders for Git repos.

---

## Git Best Practices

### Run all Git commands from the project root

Always confirm you are in the correct folder:
```bash
cd /Users/kinompungpound/Downloads/PROJEXT/opt/ems_system
pwd
git rev-parse --show-toplevel  # Should output the project path above
```

### Standard Development Workflow

```bash
# 1. Ensure you're on main and up to date
git checkout main
git pull --ff-only origin main

# 2. Create a feature branch
git checkout -b feature/<feature-name>

# 3. Make changes, check status
git status
git diff <file>  # review changes before staging

# 4. Stage and commit (only source code and tracked files)
git add <files>
git commit -m "feat: describe the change"

# 5. Push to origin
git push origin feature/<feature-name>

# 6. Open a pull request on GitHub for review
```

### Commit Message Format

Use conventional commits:
- `feat: ` for new features
- `fix: ` for bug fixes
- `chore: ` for maintenance (dependencies, config, safety notes)
- `docs: ` for documentation
- `refactor: ` for code restructuring
- `test: ` for tests

Example:
```bash
git commit -m "feat: add exam schedule import validation"
```

---

## Files to NOT Commit

The `.gitignore` file already excludes these. **Never** commit or push:

- Backend runtime database:
  - `backend/ems.db`
  - `backend/ems.db-shm`
  - `backend/ems.db-wal`
  - `backend/ems.db.bak`
- Python environment and cache:
  - `backend/.venv/`
  - `backend/__pycache__/`
  - `**/__pycache__/`
  - `*.pyc`
- Node and build artifacts:
  - `frontend/node_modules/`
  - `frontend/dist/`
  - `frontend/build/`
- Local configuration and secrets:
  - `.env` (local environment variables)
  - `.env.local`
  - `.env.*.local`
- Logs and temporary files:
  - `*.log`
  - `backend/logs/`
  - `backend/uploads/`
- Backup folders:
  - `opt/ems_system_recovery_backup_*/`
  - `*backup*/`

If you see these in `git status`, do **not** add them. They should appear as untracked or ignored files.

---

## Troubleshooting

### "Git shows home folder as repository"

This is a previous issue that has been fixed. To confirm it does not recur:

1. In VS Code, ensure you opened the project folder directly (not a parent).
2. In the integrated terminal, verify:
   ```bash
   pwd
   git rev-parse --show-toplevel
   ```
   Both should point to `/Users/kinompungpound/Downloads/PROJEXT/opt/ems_system`.

3. If the issue recurs, close VS Code, navigate to the correct folder in Terminal, and run:
   ```bash
   code /Users/kinompungpound/Downloads/PROJEXT/opt/ems_system
   ```

### "I committed a file that should be ignored"

If you accidentally committed a runtime file (e.g., `backend/ems.db`), the file can be untracked without deleting it locally:

```bash
# Remove from Git index but keep the file locally
git rm --cached backend/ems.db

# Update .gitignore if needed (it should already have rules for this)
git add .gitignore

# Commit the removal
git commit -m "chore: remove accidental runtime file from tracking"
git push origin <branch>
```

### "I need to undo a local commit"

If you made a commit locally that you haven't pushed yet:

```bash
# View recent commits
git log --oneline -5

# Undo the last commit but keep the changes
git reset HEAD~1

# Or undo the last commit and discard changes
git reset --hard HEAD~1
```

**Do NOT use `git reset` on commits already pushed to origin unless you have a very good reason and team agreement.**

---

## Useful Commands

```bash
# Check current status
git status

# Show ignored files
git status --ignored --short

# View recent commits with graph
git log --oneline --decorate --graph -10

# See differences before staging
git diff <file>

# See staged changes
git diff --cached

# Create a local branch for backup (safe; non-destructive)
git branch backup-<name>

# View all local branches
git branch -v

# View all branches including remote tracking
git branch -a
```

---

## Questions or Issues?

If you encounter Git issues or have questions about the workflow:
1. Check this README-DEV.md first.
2. Run `git status` and `git log --oneline -5` to understand the current state.
3. Do NOT use `git push -f` (force push) without explicit reason and team approval.
4. Ask a senior engineer if you are unsure.

---

**Last updated:** 2026-04-28
