# Plan: Auto-commit Script (Human-Only)

Referrence this doc in the script. So, you remember where to look for what you are doing.

## Overview
Create a human-only commit automation script at `automations/auto-commit` that builds commit messages per project conventions, optionally bumps version on completion, and only commits files the human has already staged.

## Goals
- Follow `version-control.md` commit format: `v{version}: [{status}] {task_name}` with optional body
- Support `in progress` (checkpoint) and `complete` (completion) commits
- Bump version only when completing (status=complete) and staged files exist
- Never blanket-add files; only stage bookkeeping files the script itself modifies
- Human-triggered only

## Non-Goals
- AI-triggered commits, exclude lists, destructive git ops, remote operations

## Files Affected
- `automations/auto-commit` (new)
- `backend/src/core/version.py` (updated on complete+bump)
- `RESUME-HERE.md` (updated on complete+bump - mark current item complete)
- `ROADMAP.md` (updated on complete+bump - sync version section)

## Implementation Steps

1. **Create script structure**
- Create `automations/` directory if needed (at repo root)
- Create executable shell script `automations/auto-commit`
- Use POSIX shell (`#!/bin/sh`); be portable

2. **Argument parsing**
- Flags: `-s|--status` (`complete|c|in-progress|i|in progress`), `-b|--bump` (`y|n|yes|no`), `-m|--body` (text), `-h|--help`
- Prompt for missing required args if interactive

3. **Repo root and data extraction**
- cd to repo root (`git rev-parse --show-toplevel`)
- Extract task name from `RESUME-HERE.md`: find line with `[in progress]` or `[current]`, strip markers to get task text
- Read version from `backend/src/core/version.py`: parse `__version__ = "X.Y.Z"`
- Check staged files: `git diff --cached --name-only`. If empty, error and exit

4. **Version bump logic (complete only)**
- If status is complete and bump not explicitly false: increment patch (Z+1)
- Update `backend/src/core/version.py` with new version
- Update `RESUME-HERE.md`: change current `[in progress]` to `[complete]`
- Update `ROADMAP.md`: sync corresponding version section from RESUME-HERE
- Stage modified files: `git add backend/src/core/version.py RESUME-HERE.md ROADMAP.md`

5. **Commit**
- Build header: `v{version}: [{status}] {task_name}` (use new version if bumped)
- Build commit with optional body: `git commit -m "$header" ${body:+-m "$body"}`
- Human triggered; for complete+bump this follows autonomous commit rule (human invoked). For in-progress, checkpoint commit.

6. **Error handling**
- No staged files → error, exit 1 "There are no staged files, silly."
- No current item found → error, exit 1 (Ask AI what this means before adding a qulity human message)
- Version parse/update failures → error, exit 1 "I couldn't do the version bump. So, did not commit. Check what happened."
- Git failures → report and preserve staged state "{command} failed. Did not commit"

## Validation
- In-progress with staged files: commits with `[in progress]`, no version changes
- Complete with staged files: bumps version, updates docs, stages them, commits with `[complete]` and new version
- No staged files: errors without changes
- Message format matches `version-control.md`

## Risks
- Task name extraction brittle if RESUME-HERE format changes (mitigate: simple line-based parsing)
- Version parsing assumes exact format in version.py

## Open Questions
None. Design matches simplified human-only flow.