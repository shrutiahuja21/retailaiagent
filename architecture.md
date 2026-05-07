# Retail AI Assistant Architecture

## Overview
The Retail AI Assistant is a multi-role agentic system designed to handle Personal Shopper (Revenue) and Customer Support (Operations) tasks. It utilizes a tool-calling (function calling) architecture to separate reasoning from data retrieval, ensuring high accuracy and minimizing hallucinations.

## Core Components

### 1. Data Layer & Memory Store (`data_manager.py`)
- **Responsibility**: Handles all interactions with the underlying data sources (`product_inventory.csv`, `orders.csv`, and `policy.txt`).
- **Memory Store / Caching**:
    - Implements a simple in-memory cache (`_product_cache`, `_order_cache`, `_search_cache`) to store results of expensive data operations and lookups.
    - Uses dictionary-based storage for O(1) retrieval of previously fetched products and orders.
    - Caches product search results by generating a unique key based on the applied filters, reducing processing time for repeat queries.
- **Logic**: Uses `pandas` for efficient filtering and searching. It handles complex data types like the `stock_per_size` dictionary and ensures data integrity when queried by the agent.

### 2. Tool Layer (`tools.py`)
- **Responsibility**: Provides structured interfaces for the agent to interact with data.
- **Tools**:
    - `search_products(filters)`: Implements multi-constraint search logic (tags, price, size, sale status).
    - `get_product(product_id)`: Fetches full details for a single product.
    - `get_order(order_id)`: Fetches order history.
    - `evaluate_return(order_id)`: A rule-based engine that applies the complex return policy (window checks, sale vs. clearance, vendor exceptions) to determine eligibility.
- **Design Choice**: By moving the return logic into a dedicated tool (`evaluate_return`), we reduce the reasoning burden on the LLM and ensure strict adherence to the policy rules.

### 3. Agent Layer (`agent.py`)
- **Responsibility**: Manages the conversation flow and dynamic tool selection.
- **Model Providers**:
    - **Local (Default)**: A heuristic-based reasoning engine using regular expressions and keyword matching. It extracts intent (shopping vs. support) and constraints (Order ID, size, price, tags) directly from user input. **Requires NO API key.**
    - **Gemini**: Uses `gemini-1.5-flash` for advanced natural language understanding.
    - **OpenAI**: Uses `gpt-4o` as a fallback provider.
- **System Prompt**: Enforces strict guidelines:
    - Always use tools for data.
    - Explain reasoning for recommendations.
    - Refuse requests for non-existent IDs.
    - Today's date is hardcoded to `2026-05-07` for consistent return window calculations.

### 4. UI & CLI Layers
- **CLI (`main.py`)**: Provides a simple interactive terminal interface for development and quick testing.
- **Web UI (`ui.py`)**: A modern, responsive interface built with `Streamlit`.
    - **Sidebar**: Features "Quick Examples" that allow users to trigger complex queries with a single click.
    - **Chat Interface**: Uses `st.chat_message` for a natural conversational experience.
    - **Visual Feedback**: Includes spinners and status messages to indicate when the agent is reasoning or calling tools.
    - **Styling**: Custom CSS is used to align the look and feel with the Étoile brand (pink accents, clean white layout).

## Minimizing Hallucination
Hallucination is minimized through several strategies:
1.  **Tool-First Strategy**: The agent is instructed via the system prompt to *never* assume product or order details and *always* fetch them via tools.
2.  **Structured Output**: Tools return structured JSON data, which the agent must interpret rather than "making up" information.
3.  **Strict Error Handling**: Tools explicitly return error messages for invalid IDs (e.g., "Order O9999 not found"). The agent is trained to pass these errors directly to the user.
4.  **Rule-Based Support**: Instead of asking the LLM to "read and interpret" the policy text every time, the `evaluate_return` tool handles the heavy lifting of date math and rule application, providing the agent with a definitive "Eligible/Not Eligible" status and a reason string.

## Tool Selection Process
1.  **Intent Recognition**: The LLM analyzes the user's natural language input.
2.  **Parameter Extraction**: It identifies constraints (e.g., "under $300", "size 8", "on sale") and maps them to tool parameters.
3.  **Dynamic Invocation**: The LLM decides which tool is most appropriate. If multiple tools are needed (e.g., fetching an order then checking a product), the agent can perform multiple tool calls in sequence.
4.  **Reasoning & Synthesis**: Once the tool returns data, the agent synthesizes a response that justifies its recommendation or decision based on the fetched data.

## Scalability & Future Improvements
- **External Integration**: The `DataManager` can be easily replaced with an API client for a real e-commerce backend (e.g., Shopify, BigCommerce).
- **Memory**: Implementing a conversation memory (e.g., using a vector database) would allow the agent to handle more complex, multi-turn shopping sessions.
- **Enhanced Search**: Replacing the basic CSV search with a vector search (embeddings) would improve product discovery for vague queries (e.g., "something for a summer wedding").
