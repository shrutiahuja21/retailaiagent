# Retail AI Assistant Architecture

## Overview
The Retail AI Assistant is a data-driven agentic system designed to handle Personal Shopper and Customer Support tasks. It utilizes a modular, tool-based architecture that operates entirely locally on CSV data, ensuring 100% reliability without external API dependencies or costs.

## Core Components

### 1. Data Layer & Memory Store (`data_manager.py`)
- **Responsibility**: Handles all interactions with the underlying data sources (`product_inventory.csv`, `orders.csv`, and `policy.txt`).
- **Memory Store / Caching**:
    - Implements a simple in-memory cache to store results of data operations and lookups.
    - Uses dictionary-based storage for O(1) retrieval of previously fetched products and orders.
    - Caches search results to reduce processing time for repeat queries.

### 2. Tool Layer (`tools.py`)
- **Responsibility**: Provides structured interfaces for data interaction and policy enforcement.
- **Tools**:
    - `search_products(filters)`: Implements multi-constraint search logic (tags, price, size, sale status).
    - `get_product(product_id)`: Fetches full details for a single product.
    - `get_order(order_id)`: Fetches order history.
    - `evaluate_return(order_id)`: A deterministic rule-based engine that applies the complex return policy (window checks, sale vs. clearance, vendor exceptions).

### 3. Agent Layer (`agent.py`)
- **Responsibility**: Processes natural language input using a local heuristic reasoning engine.
- **Reasoning Engine**:
    - Uses regular expressions and keyword matching to identify user intent (Shopping vs. Support).
    - Automatically extracts constraints like Order IDs, price limits, sizes, and style tags.
    - Orchestrates tool calls and synthesizes human-like responses based on retrieved data.
- **Design Choice**: By using a local engine, the system avoids hallucination, API costs, and rate limits while maintaining high accuracy for domain-specific tasks.

### 4. UI & CLI Layers
- **CLI (`main.py`)**: A simple interactive terminal interface.
- **Web UI (`ui.py`)**: A modern interface built with `Streamlit`.
    - Features "Quick Examples" for one-click testing.
    - Provides a natural conversational experience with visual feedback.

## Minimizing Hallucination
Hallucination is eliminated by:
1. **Data-First Logic**: The agent can only provide information that exists in the CSV files.
2. **Deterministic Support**: Return eligibility is calculated via a rule-based engine (`evaluate_return`), not by probabilistic model guessing.
3. **Structured Response Generation**: Responses are built directly from tool outputs, ensuring every detail (price, stock, reason) is factually accurate.
