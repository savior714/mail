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

## 🔄 Rule Synthesis Funnel (Layered Logic)
1.  **Hard Rules (Priority Engine)**: Uses a `Dict[str, List[Regex]]` in `config.py`. 
    - **Logic**: First match wins based on category order (Finance > Checkout > Dev > ...).
    - **Purpose**: High-confidence classification for known transaction/security mail.
2.  **Sync (SQLite)**: Fetch headers and size metadata via Gmail API for AI context.
3.  **Local-First AI Synthesis**: Orchestrates `gemini-1.5-flash` to classify unhandled senders. 
    - AI is tuned via a custom system prompt to follow the established priority and handle ambiguity (e.g., non-financial billing).
4.  **Cloud Apply**: High-speed, batch organization using Gmail's `batchModify`.

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
