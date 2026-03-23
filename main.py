import logging
import yaml
import os
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict

from src.api.t212_client import T212Client
from src.data.provider import DataProvider
from src.strategies.base import StrategyRegistry
from src.core.validator import SignalValidator
from src.execution.engine import ExecutionEngine
from src.utils.logger import setup_logger
from src.utils.paths import get_config_path, get_resource_path

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
    Headless entry point for the refactored Trading 212 Bot.
    Orchestrates the flow: Market Data -> Strategy -> Validation -> Execution.
    """
    # 1. Configuration & Logging
    config = load_config()
    log_file = get_resource_path(config.get("logging", {}).get("log_file", "logs/trading_bot.log"))
    log_level_name = config.get("logging", {}).get("level", "INFO")
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    logger = setup_logger("trading_bot", log_file=log_file, level=log_level)
    logger.info("Initializing Headless Trading 212 Bot...")

    # 2. Components Initialization
    api_key = os.getenv("T212_API_KEY") or config["t212"]["api_key"]
    dry_run = config["t212"]["dry_run"]
    client = T212Client(api_key=api_key, dry_run=dry_run)
    
    data_provider = DataProvider(external_api_key=config["data"].get("external_api_key"))
    validator = SignalValidator(min_confidence=0.5, min_strength=0.5)
    execution_engine = ExecutionEngine(client=client, risk_limits=config["strategy"]["risk_limits"])

    # 3. Strategy Loading
    # Dynamic strategy loading based on config or environment variable
    strategy_name = os.getenv("ACTIVE_STRATEGY") or config.get("strategy", {}).get("active_strategy")
    strategy_params = config.get("strategy", {}).get("strategy_params", {})
    tickers = config.get("strategy", {}).get("tickers", [])
    
    if not strategy_name:
        logger.error("No active strategy defined in config or environment variables.")
        return

    try:
        strategy = StrategyRegistry.get_strategy(strategy_name, tickers=tickers, **strategy_params)
        logger.info(f"Loaded strategy: {strategy_name} with parameters: {strategy_params}")
    except (ValueError, TypeError) as e:
        logger.error(f"Failed to load strategy '{strategy_name}': {e}")
        return

    # 4. Market Data Acquisition
    tickers = strategy.get_tickers()
    market_data: Dict[str, pd.DataFrame] = {}
    
    for ticker in tickers:
        try:
            # Fetch historical data (e.g., last 100 candles)
            df = data_provider.fetch_historical_candles(ticker, limit=100)
            market_data[ticker] = df
        except Exception as e:
            logger.error(f"Failed to fetch data for {ticker}: {e}")

    # 5. Signal Generation
    logger.info("Generating signals...")
    raw_signals = strategy.generate_signals(market_data)
    logger.info(f"Generated {len(raw_signals)} raw signals.")

    # 6. Signal Validation
    logger.info("Validating signals...")
    validated_signals = validator.validate_signals(raw_signals)
    logger.info(f"Validation complete: {len(validated_signals)} signals accepted.")

    # 7. Execution
    if validated_signals:
        logger.info("Executing validated signals...")
        execution_engine.process_signals(validated_signals)
    else:
        logger.info("No valid signals to execute this cycle.")

    logger.info("Bot execution cycle complete.")

if __name__ == "__main__":
    main()
