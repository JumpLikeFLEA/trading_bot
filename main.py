import logging
import yaml
import os
from dotenv import load_dotenv
from src.api.t212_client import T212Client
from src.engine.executor import Executor
from src.data.provider import DataProvider
from src.utils.logger import setup_logger
from src.utils.paths import get_config_path, get_resource_path
import pandas as pd

# Load environment variables
load_dotenv()

def load_config(config_path=None) -> dict:
    """Load configuration from a YAML file."""
    if config_path is None:
        config_path = get_config_path()
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def main():
    """
    Main entry point for the Trading 212 Bot Execution Shell.
    Demonstrates the initialization and orchestration of the bot components.
    """
    # 1. Load Configuration
    config = load_config()
    
    # 2. Setup Logging
    log_file = get_resource_path(config.get("logging", {}).get("log_file", "logs/trading_bot.log"))
    log_level_name = config.get("logging", {}).get("level", "INFO")
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    logger = setup_logger("trading_bot", log_file=log_file, level=log_level)
    logger.info("Initializing Trading 212 Bot Execution Shell...")

    # 3. Initialize API Client
    api_key = os.getenv("T212_API_KEY") or config["t212"]["api_key"]
    dry_run = config["t212"]["dry_run"]
    client = T212Client(api_key=api_key, dry_run=dry_run)
    logger.info(f"API Client initialized (Dry Run: {dry_run})")

    # 4. Initialize Data Provider
    data_provider = DataProvider(external_api_key=config["data"].get("external_api_key"))
    logger.info("Data Provider initialized.")

    # 5. Initialize Executor
    risk_limits = config["strategy"]["risk_limits"]
    executor = Executor(client=client, risk_limits=risk_limits)
    logger.info("Executor initialized.")

    # --- DEMONSTRATION: Running a strategy iteration ---
    # In a real scenario, this would be inside a loop or scheduled task.
    
    # Example Tickers from config
    tickers = config["strategy"]["tickers"]
    
    # Fetch data (Placeholder)
    # data = data_provider.fetch_historical_candles(ticker="AAPL_US_EQ", interval="1h")
    
    # Mock Signals (In a real scenario, these come from your Alpha Strategy)
    # +0.1 means Buy 10% of portfolio, -0.05 means Sell 5% of portfolio
    mock_signals = pd.DataFrame([
        {"ticker": "AAPL_US_EQ", "signal_weight": 0.1},
        {"ticker": "TSLA_US_EQ", "signal_weight": -0.05}
    ])
    
    logger.info(f"Processing {len(mock_signals)} mock signals.")
    executor.execute_signals(mock_signals)
    
    logger.info("Bot execution shell shutdown.")

if __name__ == "__main__":
    main()
