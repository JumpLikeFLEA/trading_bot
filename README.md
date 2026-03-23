# Trading 212 Bot Infrastructure (Headless)

A professional-grade, modular "Execution Shell" for Trading 212, designed for headless operation and seamless integration with Machine Learning (ML) Alphas.

## ⚠️ Safety First

**IMPORTANT: This bot operates EXCLUSIVELY in Practice Mode.**
- The base URL is hardcoded to `https://demo.trading212.com/api/v0`.
- **Practice Mode Only:** This is for educational and testing purposes. Do not attempt to use this with real funds unless you have thoroughly audited the code and modified the endpoints (at your own risk).
- **API Key Security:** You are solely responsible for your API keys. Never commit your `.env` file or hardcode keys into the source code.

## 🏗️ Architecture Overview

The project follows a strict separation of concerns for headless operation:

- `src/api/`: **High-Level API Client**. Handles REST communication, rate limiting (429), and maintenance modes (503).
- `src/engine/`: **Execution Logic**. Bridges signals from Alphas to the API, handles order sizing and ticker mapping.
- `src/data/`: **Data Ingestion**. Fetches historical and real-time data (Yahoo Finance / Alpha Vantage placeholders).
- `config/`: Centralized YAML configuration for tickers, risk limits, and logging.

```text
trading_bot/
├── config/             # Settings & Risk Limits
├── src/
│   ├── api/            # T212 REST Wrapper
│   ├── engine/         # Strategy ABC & Executor
│   ├── data/           # Data Providers
│   └── utils/          # Logging & Path Helpers
└── main.py             # Headless Entry Point
```

## 🚀 Setup Instructions

### 1. Environment Setup
Clone the repository and install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file in the root directory and add your Trading 212 Practice API Key:
```text
T212_API_KEY=your_practice_api_key_here
```

Adjust trading parameters in `config/settings.yaml`.

### 3. Running the Bot
To launch the **Headless Bot**:
```bash
python main.py
```

## 🖥️ Headless Monitoring

The bot logs all critical events to both the console and a file:
- **Trade Executions**: Logged with ticker, quantity, and status.
- **Account Status**: Regular updates on equity and free cash.
- **API Health**: Monitoring for rate limits and maintenance windows.

Logs are stored by default in `logs/trading_bot.log`.

## 🛠️ Build Pipeline (Windows EXE)

The project is configured for Nuitka to generate a standalone Windows executable.
To build the `.exe`:
```powershell
./build_exe.ps1
```
This will generate a `dist/` folder containing the `TradingBot.exe`.

---
*Disclaimer: Trading involves risk. Use this bot responsibly in practice mode.*
