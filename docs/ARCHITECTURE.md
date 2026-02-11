# Architecture & Implementation (Web Pivot)

## 🏗️ Core Architecture: Decoupled Web Stack
The project migrated from a monolithic TUI/GUI to a modern, decoupled web architecture:

1.  **Frontend (React + Tailwind v4)**
    - **Aesthetic**: Custom "Hand-Drawn" theme using `Patrick Hand` font and sketchy CSS borders.
    - **Engine**: Tailwind CSS v4 with Vite-native processing.
    - **Routing**: `react-router-dom` for application navigation.
    - **State**: Centralized dashboard and live pipeline logging.

2.  **Backend (FastAPI)**
    - **REST API**: Exposes core organization logic as JSON endpoints.
    - **Middleware**: CORS handling for the React frontend.
    - **Persistence**: SQLite (via `peewee`) for local metadata storage.

## 🔄 Rule Synthesis Funnel
1.  **Sync (SQLite)**: Fetch headers and size metadata via Gmail API.
2.  **Logic Synthesis (AI)**: SQL aggregation + Gemini classification to generate `rules.json`.
3.  **Cloud Apply**: High-speed organization of the mailbox using Gmail's `batchModify`.

## Module Responsibilities

### `src.api.main`
- Primary entry point for the FastAPI server.
- Handles requests for stats, rule management, and pipeline execution.

### `src.services.syncer`
- Handles Gmail -> SQLite synchronization with batch filtering.

### `src.services.rule_generator`
- Orchestrates AI classification and rule persistence.

### `src.services.gmail_applier`
- Manages Gmail label creation and high-performance organization.

### `frontend/src/`
- Contains all UI components and pages (Dashboard, Rules, Pipeline, Settings).
