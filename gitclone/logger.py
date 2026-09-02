"""
Logging configuration for GitClonePro
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Color codes for terminal output
COLORS = {
    "DEBUG": "\033[36m",    # Cyan
    "INFO": "\033[32m",     # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",    # Red
    "SUCCESS": "\033[92m",  # Bright Green
    "RESET": "\033[0m",     # Reset
}

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)

def setup_logger(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    console: bool = True
) -> logging.Logger:
    """
    Set up the logger

    Args:
        log_file: Path to log file
        log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        console: Enable console output

    Returns:
        Logger instance
    """
    logger = logging.getLogger("gitclone")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_formatter = ColoredFormatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

# Global logger instance
_logger = None

def get_logger() -> logging.Logger:
    """Get the global logger instance"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger

def log(message: str, level: str = "INFO"):
    """
    Log a message

    Args:
        message: Message to log
        level: Log level (DEBUG, INFO, WARNING, ERROR, SUCCESS)
    """
    logger = get_logger()
    level = level.upper()

    if level == "SUCCESS":
        logger.info(f"✓ {message}")
    elif level == "ERROR":
        logger.error(f"✗ {message}")
    elif level == "WARNING":
        logger.warning(f"⚠ {message}")
    elif level == "DEBUG":
        logger.debug(message)
    else:
        logger.info(f"• {message}")