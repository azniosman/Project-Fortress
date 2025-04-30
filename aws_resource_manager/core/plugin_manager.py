#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Plugin Manager - Manages service modules for AWS resource operations

This module provides functionality to discover, load, and manage service modules
for different AWS services.
"""

import os
import sys
import importlib
import importlib.util
import inspect
import logging
from typing import Dict, List, Any, Optional, Set

from core.config_manager import ConfigManager
from utils.logger import setup_logger

class ServiceModule:
    """
    Base class for all service modules
    
    This class defines the interface that all service modules must implement.
    """
    
    def __init__(self, service_name: str, service_display_name: str):
        """
        Initialize the service module
        
        Args:
            service_name: The internal name of the service (e.g., 'ec2')
            service_display_name: The display name of the service (e.g., 'EC2')
        """
        self.service_name = service_name
        self.service_display_name = service_display_name
        self.logger = setup_logger(f"service.{service_name}")
    
    def get_service_name(self) -> str:
        """
        Get the service name
        
        Returns:
            The service name
        """
        return self.service_name
    
    def get_service_display_name(self) -> str:
        """
        Get the service display name
        
        Returns:
            The service display name
        """
        return self.service_display_name
    
    def get_operations(self) -> List[str]:
        """
        Get the list of operations supported by this service module
        
        Returns:
            List of operation names
        """
        raise NotImplementedError("Service modules must implement get_operations")
    
    def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an operation on this service
        
        Args:
            operation: The operation to execute
            **kwargs: Operation-specific parameters
            
        Returns:
            Dictionary with operation result
        """
        raise NotImplementedError("Service modules must implement execute_operation")

class PluginManager:
    """
    Manages service modules for AWS resource operations
    
    This class is responsible for discovering, loading, and managing service modules
    for different AWS services.
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        Initialize the plugin manager
        
        Args:
            config_manager: The configuration manager
        """
        self.config_manager = config_manager
        self.service_modules: Dict[str, ServiceModule] = {}
        self.logger = setup_logger(__name__)
    
    def discover_plugins(self) -> None:
        """
        Discover and load all available service modules
        """
        self.logger.info("Discovering service modules...")
        
        # Get the modules directory
        modules_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "modules"
        )
        
        # Discover service categories
        for category in os.listdir(modules_dir):
            category_dir = os.path.join(modules_dir, category)
            
            if not os.path.isdir(category_dir) or category.startswith("_"):
                continue
            
            # Discover service modules in this category
            for filename in os.listdir(category_dir):
                if not filename.endswith(".py") or filename.startswith("_"):
                    continue
                
                module_name = filename[:-3]  # Remove .py extension
                module_path = os.path.join(category_dir, filename)
                
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(
                        f"modules.{category}.{module_name}",
                        module_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find service module classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and
                            issubclass(obj, ServiceModule) and
                            obj is not ServiceModule):
                            
                            # Instantiate the service module
                            service_module = obj()
                            service_name = service_module.get_service_name()
                            
                            # Register the service module
                            self.service_modules[service_name] = service_module
                            self.logger.info(f"Loaded service module: {service_name}")
                
                except Exception as e:
                    self.logger.error(f"Error loading module {module_name}: {str(e)}")
        
        self.logger.info(f"Discovered {len(self.service_modules)} service modules")
    
    def get_service_module(self, service_name: str) -> Optional[ServiceModule]:
        """
        Get a service module by name
        
        Args:
            service_name: The name of the service
            
        Returns:
            The service module, or None if not found
        """
        return self.service_modules.get(service_name)
    
    def get_all_service_modules(self) -> List[ServiceModule]:
        """
        Get all registered service modules
        
        Returns:
            List of all service modules
        """
        return list(self.service_modules.values())
    
    def get_available_services(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get available services grouped by category
        
        Returns:
            Dictionary mapping category to list of services
        """
        services_by_category: Dict[str, List[Dict[str, str]]] = {}
        
        for service_name, module in self.service_modules.items():
            # Determine the category from the module path
            module_path = inspect.getmodule(module).__file__
            relative_path = os.path.relpath(
                module_path,
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            
            parts = relative_path.split(os.sep)
            if len(parts) >= 2 and parts[0] == "modules":
                category = parts[1]
            else:
                category = "other"
            
            # Add the service to the category
            if category not in services_by_category:
                services_by_category[category] = []
            
            services_by_category[category].append({
                "name": service_name,
                "display_name": module.get_service_display_name()
            })
        
        return services_by_category
    
    def check_plugins(self) -> List[str]:
        """
        Check for issues with loaded plugins
        
        Returns:
            List of issues found (empty if no issues)
        """
        issues = []
        
        for service_name, module in self.service_modules.items():
            try:
                # Check if operations list is implemented
                operations = module.get_operations()
                
                # Check if execute_operation is implemented for each operation
                for operation in operations:
                    try:
                        # Just check if the method exists and is callable
                        if not hasattr(module, operation) or not callable(getattr(module, operation)):
                            issues.append(f"Service '{service_name}' declares operation '{operation}' but doesn't implement it")
                    except Exception as e:
                        issues.append(f"Error checking operation '{operation}' in service '{service_name}': {str(e)}")
            
            except Exception as e:
                issues.append(f"Error checking service module '{service_name}': {str(e)}")
        
        return issues 