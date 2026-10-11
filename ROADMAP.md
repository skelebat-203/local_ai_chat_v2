# Roadmap — Lex: Local Chat Bot v2

## Scope
A local-first chat interface with subject/persona management, chat logging, and a PyWebView UI. Runs entirely on the user's machine via Ollama.

## Phases & Milestones

### v0.1 — Foundation (COMPLETED)
- [x] Core chat with Ollama (llama3 default)
- [x] Subject/persona system (CRUD)
- [x] Chat logging per subject (markdown files)
- [x] Command handler (`/subject`, `/persona`, `/chat`, `/swap`, etc.)
- [x] Basic PyWebView UI
- [x] File watcher for AI-assisted development
- [x] Unit tests (chat, retriever, logger)

### v0.2 — Subject Source Docs (IN PROGRESS)
1. [ ] **[in progress]** preflight stuff
2. [ ] Subject source documents CRUD
3. [ ] Source doc retrieval integrated into chat context
4. [ ] UI: subject panel with source doc management

### v0.3 — Chat History Management
- [ ] Chat history panel (screen/panel/accordion/modal)
- [ ] Auto-generate chat titles (first 10 words, underscore format)
- [ ] Disambiguation suffix (-01, -02) for duplicate titles
- [ ] Full CRUD for chat history entries

### v0.4 — Enhanced UI
- [ ] Improved PyWebView layout/styling
- [ ] Keyboard navigation (prompt_toolkit integration)
- [ ] Responsive subject/chat panels

### v0.5 — Web Search & Source Links
- [ ] Local web search integration
- [ ] Source links CRUD per subject
- [ ] Citation display in chat responses

### v1.0 — VSCodium/VS Code Extension (Optional Investigation)
- [ ] Workspace-scoped file CRUD
- [ ] Explicit user approval for edits/terminal commands
- [ ] Least-privilege permissions policy
- [ ] Auditable action history

---

## Versioning
Follows `v{major}.{subversion}.{completed-item}` per project versioning doc.
Current version: **v0.2.0** (starting v0.2, item 0 completed)

## Notes
- This project is **local-only** (not network-exposed). Uses `issue-severity-matrix_LOCAL.md`.
- If network exposure is ever added, must switch to `issue-severity-matrix_NETWORKED.md` and re-rate all `NETWORK-ONLY` findings.