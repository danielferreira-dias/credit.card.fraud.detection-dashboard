import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class Logger:
    """
    Logger configuration for the agent service.
    Provides structured logging with different levels and output formats.
    """

    def __init__(self, name: str = "agent_service", level: str = "INFO", log_file: Optional[str] = None):
        """
        Initialize the logger.

        Args:
            name: Logger name
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional log file path. If None, logs only to console.
        """
        self.name = name
        self.level = getattr(logging, level.upper())
        self.log_file = log_file
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup and configure the logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if self.log_file:
            # Create directory if it doesn't exist
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(self.level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self.logger

    def log_agent_action(self, action: str, details: dict = None):
        """Log agent-specific actions with structured data."""
        message = f"Agent Action: {action}"
        if details:
            detail_str = ", ".join([f"{k}={v}" for k, v in details.items()])
            message += f" | Details: {detail_str}"
        self.logger.info(message)

    def log_tool_usage(self, tool_name: str, parameters: dict = None, result_summary: str = None):
        """Log tool usage with parameters and results."""
        message = f"Tool Used: {tool_name}"
        if parameters:
            param_str = ", ".join([f"{k}={v}" for k, v in parameters.items()])
            message += f" | Parameters: {param_str}"
        if result_summary:
            message += f" | Result: {result_summary}"
        self.logger.info(message)

    def log_error(self, error: Exception, context: str = None):
        """Log errors with context information."""
        message = f"Error occurred: {str(error)}"
        if context:
            message += f" | Context: {context}"
        self.logger.error(message, exc_info=True)

    def log_query(self, query: str, response_summary: str = None):
        """Log user queries and response summaries."""
        message = f"User Query: {query}"
        if response_summary:
            message += f" | Response Summary: {response_summary}"
        self.logger.info(message)


def get_agent_logger(
    name: str = "agent_service",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Factory function to get a configured agent logger.

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    agent_logger = Logger(name=name, level=level, log_file=log_file)
    return agent_logger.get_logger()


# Default logger instance
default_logger = get_agent_logger()