#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logger Utility - Provides logging functionality

This module provides a consistent logging setup across the application,
including log formatting, file logging, and log rotation.
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(
    name: str,
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_to_console: bool = True,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up and configure a logger
    
    Args:
        name: Name of the logger
        log_level: Logging level
        log_file: Optional log file path
        log_to_console: Whether to log to console
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Set the logging level
    logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    
    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Add console handler if requested
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_log_file_path(
    logger_name: str,
    base_dir: Optional[str] = None
) -> str:
    """
    Get the log file path for a logger
    
    Args:
        logger_name: Name of the logger
        base_dir: Optional base directory for logs
        
    Returns:
        Log file path
    """
    # Determine base directory
    if base_dir is None:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_dir = os.path.join(app_dir, "logs")
    
    # Ensure logs directory exists
    os.makedirs(base_dir, exist_ok=True)
    
    # Convert logger name to file name (replace dots with underscores)
    file_name = f"{logger_name.replace('.', '_')}.log"
    
    return os.path.join(base_dir, file_name)

def configure_root_logger(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None
) -> None:
    """
    Configure the root logger
    
    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Set up the logger
    setup_logger(
        name="",  # Root logger has empty name
        log_level=log_level,
        log_file=log_file,
        log_to_console=True
    ) 