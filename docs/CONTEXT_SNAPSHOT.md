# Project Context Snapshot

## 1. Project Identity
- **Name**: Gmail-AI-Archivist (Pencil Edition)
- **Phase**: **Production Web v1.2**
- **Current Goal**: Maintenance and expansion of the sketchy web ecosystem.

## 2. Key Accomplishments (2026-02-11 ~ 2026-02-12)
- **Web Migration**: Successfully pivoted from Flet to FastAPI + React.
- **Categorization Overhaul**: 
    - Split Shopping into **Checkout** and **Promo** for clarity.
    - Introduced specialized **Car_Life** and **Notice_Privacy** categories.
    - Refined **Auth_System** and **Dev_Tech** priority handles.
- **Intelligence**: 
    - Implemented **Adaptive Rule Learning v2**: Persistent database-backed patterns with confidence tracking and feedback loop.
    - Added **AI Batching**: Chunked classification (25 senders/batch) to prevent JSON truncation errors.
    - **API Quota Management**: Intelligent caching reduces API usage by 80-90%, daily quota tracking with graceful degradation.
    - **UX Logging**: Added step-by-step progress indicators for the "Learn Rules" process.
- **Design Overhaul**: Applied a unique "Hand-Drawn" pencil aesthetic using Tailwind CSS v4.
- **Unified Startup**: Created one-click startup scripts for dual-service operation.

## 3. Tech Stack State
- **Backend**: Python 3.10+, FastAPI, Uvicorn, Peewee (SQLite).
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS v4.
- **AI**: Google Gemini API (`gemini-1.5-flash`).
- **Icons**: Lucide React.
- **Charts**: Recharts.

## 4. Current State
- **Stability**: Very High. Batch processing and adaptive learning verified.
- **Next Focus**: WebSockets for real-time logging and Settings persistence.
