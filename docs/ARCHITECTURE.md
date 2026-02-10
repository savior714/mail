# Architecture & Implementation (Production Pivot)

## Core Logic: Rule Synthesis Funnel
To overcome Gemini's 15 RPM free tier limit and handle massive historical data, we use a **"Logic Synthesis"** approach:

1.  **Step 1: Local Sync (SQLite)**
    - **Goal**: Fast, persistent storage of headers and size metadata.
    - **Mechanism**: Fetch metadata (Sender, Subject, Date, sizeEstimate) via Gmail API and store in `emails.db`.
    - **Scale**: Supports `--year` batching to reduce sync overhead.

2.  **Step 2: AI Rule Generation (Logic Synthesis)**
    - **Goal**: Classify *Senders* at scale with minimal AI cost.
    - **Mechanism**: SQL aggregation groups distinct senders.
    - **Schema**: `rules.json` stores categories along with `count` and `last_date` for audit.
    - **Override**: Manual edits in `rules.json` are preserved across runs.

3.  **Step 3: Gmail Applier (Cloud Push)**
    - **Goal**: Safe, high-speed organization of the live mailbox.
    - **Safety**: Labels are applied with a session-based tag (`History/Batch_YYYYMMDD`).
    - **Efficiency**: Uses Gmail `batchModify` to apply labels to 500 emails per request.
    - **Storage**: Detects large emails (>= 5MB) in Promo categories and flags them with `⚠️_Big_Trash`.

## Module Responsibilities

### `src.models`
- Peewee-based SQLite model (`Email`).
- Tracks category, rule source, and message size.

### `src.services.syncer`
- Handles Gmail -> SQLite synchronization with batch date filtering.

### `src.services.rule_generator`
- Orchestrates the AI synthesis and rule persistence.

### `src.services.gmail_applier`
- Manages Gmail label creation and high-performance `batchModify` operations.

### `src.main`
- Primary Production TUI providing a unified dashboard for all stages (formerly `main_local`).
