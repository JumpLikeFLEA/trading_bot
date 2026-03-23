import logging
import os
from typing import Optional

def setup_logger(name: str, log_file: str = "trading_bot.log", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up a logger with both console and file handlers.
    
    Args:
        name: Name of the logger.
        log_file: Path to the log file.
        level: Logging level.
        
    Returns:
        logging.Logger: Configured logger.
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding multiple handlers if already setup
    if not logger.handlers:
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
