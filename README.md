# Trading 212 Bot Infrastructure (Headless & Extensible)

A professional-grade, modular "Execution Shell" for Trading 212, designed for headless operation and seamless integration with Machine Learning (ML) Alphas. This architecture allows you to easily plug in new strategies without touching the core execution logic.

## ⚠️ Safety First

**IMPORTANT: This bot operates EXCLUSIVELY in Practice Mode.**
- The base URL is hardcoded to `https://demo.trading212.com/api/v0`.
- **Practice Mode Only:** This is for educational and testing purposes. Do not attempt to use this with real funds unless you have thoroughly audited the code and modified the endpoints (at your own risk).
- **API Key Security:** You are solely responsible for your API keys. Never commit your `.env` file or hardcode keys into the source code.

## 🏗️ Extensible Architecture

The project follows a modular design to separate signal generation from trade execution:

- `src/signals/`: **Signal Schema**. Defines the standardized `Signal` object using Pydantic.
- `src/strategies/`: **Alpha Strategy Layer**. Contains the base class for strategies and individual strategy implementations.
- `src/core/`: **Validation Layer**. Checks signals for quality (confidence/strength) before they reach the engine.
- `src/execution/`: **Execution Engine**. Converts validated signals into Trading 212 orders.
- `src/api/`: **T212 Client**. Low-level API communication.
- `src/data/`: **Data Provider**. Fetches market data for strategies.

```text
trading_bot/
├── config/             # YAML Settings & Risk Limits
├── src/
│   ├── api/            # T212 REST Wrapper
│   ├── core/           # Validation Logic
│   ├── data/           # Market Data Providers
│   ├── execution/      # Execution Engine
│   ├── signals/        # Signal Data Models
│   ├── strategies/     # Alpha Strategy Implementations
│   └── utils/          # Logging & Path Helpers
├── tests/              # Unit Tests
└── main.py             # Orchestration Entry Point
```

## 🚀 How to Add a New Alpha

Adding a new strategy is seamless:

1.  **Create your strategy file**: Add a new Python file in `src/strategies/` (e.g., `my_custom_alpha.py`).
2.  **Inherit and Register**:
    ```python
    from src.strategies.base import StrategyBase, StrategyRegistry
    from src.signals.models import Signal, SignalSide

    @StrategyRegistry.register("MyCustomAlpha")
    class MyCustomAlpha(StrategyBase):
        def generate_signals(self, market_data):
            # Your logic here
            return [Signal(...)]
    ```
3.  **Update `main.py`**: Change `strategy_name = "MyCustomAlpha"`.

## 📡 Signal Contract

Every strategy must return a list of `Signal` objects:
- `symbol`: Ticker symbol.
- `side`: BUY, SELL, or HOLD.
- `strength`: Normalized value (0.0 to 1.0).
- `confidence`: Confidence score (0.0 to 1.0).
- `timestamp`: Generation time.
- `strategy_name`: Name of the alpha.

## ⚙️ Setup & Execution

### 1. Environment Setup
```bash
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your T212 Practice API Key:
```text
T212_API_KEY=your_practice_api_key_here
```

### 3. Running the Bot
```bash
python main.py
```

### 4. Running Tests
```bash
pytest
```

## 🛠️ Build Pipeline
To build the standalone Windows `.exe`:
```powershell
./build_exe.ps1
```

---
*Disclaimer: Trading involves risk. Use this bot responsibly in practice mode.*
