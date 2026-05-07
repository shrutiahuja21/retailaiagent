# Retail AI Assistant (Étoile)

An intelligent agentic AI system that simulates a Personal Shopper and Customer Support Assistant for a retail environment. This project uses a modular architecture with structured tool-calling and a local heuristic reasoning engine to ensure reliability and performance.

## 🚀 Features

- **Personal Shopper (Revenue Agent)**: Recommends products based on constraints like size, price, tags, and sale status. Prioritizes bestsellers and explains recommendations.
- **Customer Support (Operations Agent)**: Evaluates return eligibility based on a complex policy involving time windows, clearance rules, and vendor exceptions.
- **Multi-Model Support**:
  - **Local Engine (Default)**: No-API-key required reasoning using heuristics and regex.
  - **Gemini 1.5 Flash**: Advanced natural language understanding via Google's generative AI.
  - **GPT-4o**: High-fidelity reasoning via OpenAI.
- **Memory Store & Caching**: In-memory caching for product lookups and searches to optimize performance.
- **Modern Web UI**: Built with Streamlit for a beautiful, responsive experience.

## 🛠️ Architecture

The system is built with a clear separation of concerns:
1. **Data Layer (`data_manager.py`)**: Handles CSV parsing, inventory management, and in-memory caching.
2. **Tool Layer (`tools.py`)**: Implements the logic for product searching and the rule-based return evaluation engine.
3. **Agent Layer (`agent.py`)**: Manages intent recognition and model provider orchestration.
4. **UI Layer (`ui.py` & `main.py`)**: Provides Streamlit web and CLI interfaces.

See [architecture.md](architecture.md) for a deep dive into the design decisions.

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/shrutiahuja21/retailaiagent.git
   cd retailaiagent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set up API keys in a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_key
   GEMINI_API_KEY=your_gemini_key
   ```

## 🖥️ Usage

### Web Interface (Recommended)
```bash
streamlit run ui.py
```

### CLI Interface
```bash
python main.py
```

## 📄 Data Files
- `product_inventory.csv`: Full list of available items, stock levels, and bestseller scores.
- `orders.csv`: Historical customer orders.
- `policy.txt`: Plain-text return and exchange policy rules.

## ⚖️ License
MIT
