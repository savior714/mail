# Architecture & Implementation

## Core Logic: 3-Layer Filtering
To balance accuracy and cost, we use a funnel approach:

1.  **Layer 1: Hard Rules (Regex)**
    - **Goal**: Handle 60-80% of automated emails (Notifications, Newsletters, Auth codes).
    - **Mechanism**: Match Sender/Subject against pre-defined regex patterns in `src/config.py`.
    - **Cost**: $0.

2.  **Layer 2: AI Classification (LLM)**
    - **Goal**: Classify personal, work, or ambiguous emails.
    - **Mechanism**: Send `Sender`, `Subject`, and `Snippet` (not full body) to GPT-4o-mini.
    - **Format**: Structured JSON Output.
    - **Cost**: Low (Mini model + Token optimization).

3.  **Layer 3: Fallback**
    - **Goal**: Safety net.
    - **Mechanism**: If AI confidence is low or format fails, mark as `Unclassified`.

## Module Responsibilities

### `src.services.gmail_client`
- Handles OAuth2 authentication.
- Manages `token.json` lifecycle.
- Fetches emails with pagination support.

### `src.services.classifier`
- Implements the 3-Layer logic.
- Manages OpenAI client interaction.

### `src.services.reporter`
- Aggregates results.
- Exports to `dry_run_report_{timestamp}.json`.

## Configuration (`src/config.py`)
- **Categories**:
    - `💰_Finance`
    - `🏥_Medical_Work`
    - `💻_Dev_Tech`
    - `🛒_Shopping_Promo`
    - `🔒_Auth_System`
    - `🏠_Personal_Life`
- **Regex Rules**: Dictionaries mapping Categories to Regex patterns.
