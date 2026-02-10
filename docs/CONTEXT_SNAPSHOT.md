# Project Context Snapshot

## 1. Project Identity
- **Name**: Gmail-AI-Archivist
- **Phase**: **Production Ready** (v1.0)
- **Current Goal**: Enable user to organize 10+ years of emails safely and efficiently.

## 2. Key Accomplishments (2026-02-10~11)
- **Repo Setup**: Initialized Git, linked to `savior714/mail`, added `skills` submodule.
- **Migration**: Switched to Google Gemini Flash (`gemini-flash-latest`).
- **Arch Pivot**: Adopted "Local-First AI Archivist" strategy (Sync -> SQLite -> AI Rule Gen -> Local Apply).
- **Implementation**: Created `src/main_local.py` (TUI), `Email` model (`peewee`), and rule synthesis logic.
- **Automation**: Implemented "Monthly Full Auto Pipeline" ([a] option) which automates Sync, AI Analysis, Local Apply, and Cloud Sync in one flow.
- **Optimization**: Enabled unlimited sender analysis in `RuleGenerator` and pagination support in `GmailClient`.
- **Simplification**: Removed `History/Batch` tags for cleaner Gmail organization; retained `⚠️_Big_Trash` flagging.
- **Documentation**: Fully refactored `README.md`, `ARCHITECTURE.md`, and `USAGE.md` for production.

## 3. Tech Stack State
- **Python**: 3.10+
- **Database**: SQLite3 (via `peewee` ORM)
- **TUI**: `rich` (Console UI + Progress bars)
- **LLM**: Google Gemini API (`google-generativeai`)
- **API**: Gmail API (`google-api-python-client`) with `modify` scope.

## 4. Current State
- **Stability**: Verified E2E flow (Sync -> AI Audit -> Cloud Apply).
- **Privacy**: `.gitignore` configured to protect `emails.db`, `token.json`, and `.env`.
