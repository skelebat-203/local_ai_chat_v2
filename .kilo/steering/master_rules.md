# Project Rules — Lex: Local Chat Bot v2

## Project-Specific Conventions

### Architecture
- **Backend**: Python 3.10+, Ollama client, prompt_toolkit, watchdog, pywebview
- **Frontend**: Single HTML file (`frontend/index.html`) served via PyWebView
- **Data**: Markdown files under `backend/data/subjects/{subject}/` and `backend/data/personas/`
- **No network exposure** — local-only threat model

### Versioning
- Scheme: `v{major}.{subversion}.{completed-item}` (see `versioning.md`)
- Current: **v0.2.0** (major=0, subversion=2, item=0)
- Update `backend/src/core/version.py` AND root `package.json` (if added) together
- Version bump = commit (autonomous per `version-control.md`)

### Commands
- All user-facing commands prefixed with `/` (e.g., `/subject`, `/persona`, `/chat`, `/swap`, `/source`)
- Command handlers in `backend/src/commands/`
- Add new commands to `command_handler.py` registry

### Testing
- Unit tests in `backend/tests/` (pytest)
- Run: `cd backend && python -m pytest tests/ -v`
- Test files: `test_chat.py`, `test_retriever.py`, `test_logger.py`

### Security
- **Local-only project** → uses `issue-severity-matrix_LOCAL.md`
- `NETWORK-ONLY` findings tracked but rated Low
- **Hard stop**: if network exposure ever proposed, must surface all `NETWORK-ONLY` findings and switch to `issue-severity-matrix_NETWORKED.md` before proceeding

### Git
- Local repo only — no remote, no push (per `version-control.md`)
- Branch: `main` (currently on `chore/re-entry-preflight`)
- Commit on every version bump; ask before checkpoint commits
- Stage specific files only (`git add <file>...`), never `git add .`
- `.gitignore` covers: logs, chat data, `__pycache__`, `.venv`, `.local`, test output, AI watcher output

### Python Conventions
- Type hints on all public functions
- Docstrings on modules/classes/functions
- Named constants at top of file (per `dev-environment.md` — no magic literals)
- Config in `backend/src/core/config.py`

### File Watcher (AI Assistant)
- `backend/src/utils/file_watcher.py` watches `backend/src/**/*.py`
- Outputs timestamped copies to `backend/src/utils/for_ai/`
- **Development aid only** — not for production
- Excluded from git via `.gitignore`

## Pointers to Global Rules
- Persona & communication: `/home/shash/Documents/AI_rules/global/base-PERSONA.md`
- Progress updates: `/home/shash/Documents/AI_rules/global/workflow-progress-updates.md`
- Versioning: `/home/shash/Documents/AI_rules/versioning_instructions/versioning.md`
- Version control: `/home/shash/Documents/AI_rules/versioning_instructions/version-control.md`
- Severity matrix (LOCAL): `/home/shash/Documents/AI_rules/project_level_instructions/issue-severity-matrix_LOCAL.md`
- Dev environment: `/home/shash/Documents/AI_rules/project_level_instructions/dev-environment.md`
- Troubleshooting: `/home/shash/Documents/AI_rules/project_level_instructions/troubleshooting.md`
- Security report style: `/home/shash/Documents/AI_rules/project_level_instructions/security-report-style.md`
- Project start: `/home/shash/Documents/AI_rules/project_level_instructions/project-start.md`

## AI Assistant behavior
- your goal across **ALL** agents is to guide and teach the user how to do the job.  
- **MUST NOT** write code or display code blocks.
- **MUST NOT** edit files.
- **MUST** guide the user to solutions. 
- **One caveat** Only **AFTER** guiding the user **AND** the user explicitly requests the answer, give them the solution.
- Files the user explicitly indicates go in `/docs/` **MUST** be allowed to be created, stored in the specified location, and follow the project naming convention of `{nnnn}-{doc_title}.md` (where applicable). If the user asks you to create a file (including PNG, JPG, JPEG, MD, TXT, JSON, YAML, etc.) that will be placed in the `/docs/` directory, you have permission to create and write that file in the specified location following the appropriate naming convention for that file type.