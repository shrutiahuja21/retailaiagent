# Retail AI Assistant (Étoile)

An intelligent data-driven AI system that simulates a Personal Shopper and Customer Support Assistant for a retail environment. This project operates entirely **locally** on CSV data, ensuring 100% reliability, zero API costs, and no hallucination.

## 🚀 Features

- **Personal Shopper (Revenue Agent)**: Recommends products based on constraints like size, price, tags, and sale status. Prioritizes bestsellers and explains recommendations.
- **Customer Support (Operations Agent)**: Evaluates return eligibility based on a deterministic policy engine (time windows, clearance rules, vendor exceptions).
- **Local Reasoning Engine**: No API keys required. Uses heuristic logic and regex to process natural language queries directly against the data store.
- **Memory Store & Caching**: In-memory caching for high-speed data retrieval.
- **Modern Web UI**: A clean, responsive interface built with Streamlit.

## 🛠️ Architecture

The system follows a modular architecture:
1. **Data Layer (`data_manager.py`)**: CSV parsing and caching.
2. **Tool Layer (`tools.py`)**: Business logic and policy enforcement.
3. **Agent Layer (`agent.py`)**: Local intent recognition and reasoning.
4. **UI Layer (`ui.py` & `main.py`)**: Web and CLI interfaces.

See [architecture.md](architecture.md) for more details.

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

**Note**: No API keys or `.env` files are required for this version.

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
- `product_inventory.csv`: Full list of available items and stock levels.
- `orders.csv`: Historical customer orders.
- `policy.txt`: Return and exchange policy rules.

## ⚖️ License
MIT
