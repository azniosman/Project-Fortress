#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Manager - Handles configuration settings and templates

This module provides functionality to load, manage, and validate configuration
settings and templates for AWS resources.
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional, Set, Union
from pathlib import Path

from utils.logger import setup_logger

class ConfigManager:
    """
    Handles configuration settings and templates
    
    This class is responsible for loading, managing, and validating configuration
    settings and templates for AWS resources.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager
        
        Args:
            config_file: Optional path to a custom config file
        """
        self.logger = setup_logger(__name__)
        
        # Determine the base directory
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Set up paths
        self.config_dir = os.path.join(self.base_dir, "config")
        self.templates_dir = os.path.join(self.base_dir, "templates")
        
        # Ensure directories exist
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Load configuration
        self.config_file = config_file or os.path.join(self.config_dir, "settings.yaml")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from the config file
        
        Returns:
            Configuration dictionary
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = yaml.safe_load(f)
                    self.logger.info(f"Loaded configuration from {self.config_file}")
                    return config or {}
            else:
                self.logger.warning(f"Config file {self.config_file} not found, using defaults")
                return self.create_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return self.create_default_config()
    
    def create_default_config(self) -> Dict[str, Any]:
        """
        Create default configuration
        
        Returns:
            Default configuration dictionary
        """
        default_config = {
            "general": {
                "log_level": "info",
                "log_directory": os.path.join(self.base_dir, "logs"),
                "state_file": os.path.join(self.config_dir, "state.json")
            },
            "aws": {
                "region": "us-east-1",
                "profile": "default",
                "retry_max_attempts": 5,
                "retry_mode": "adaptive"
            },
            "ui": {
                "color_scheme": "default",
                "show_progress_bars": True,
                "prompt_confirmations": True
            },
            "templates": {
                "directory": self.templates_dir
            },
            "security": {
                "encrypt_state_file": True,
                "credentials_timeout": 3600
            }
        }
        
        # Save the default config
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                yaml.dump(default_config, f, default_flow_style=False)
                self.logger.info(f"Created default configuration at {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving default config: {str(e)}")
        
        return default_config
    
    def get_config(self, section: Optional[str] = None, key: Optional[str] = None) -> Any:
        """
        Get configuration value
        
        Args:
            section: Optional section name
            key: Optional key within the section
            
        Returns:
            Configuration value, section, or entire config
        """
        if section is None:
            return self.config
        
        section_data = self.config.get(section, {})
        
        if key is None:
            return section_data
        
        return section_data.get(key)
    
    def set_config(self, section: str, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            section: Section name
            key: Key within the section
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            
            # Save the updated config
            with open(self.config_file, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
                self.logger.info(f"Updated configuration: {section}.{key}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error updating config: {str(e)}")
            return False
    
    def load_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load YAML file
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Loaded YAML data as dictionary
        """
        try:
            with open(file_path, "r") as f:
                data = yaml.safe_load(f)
                return data or {}
        except Exception as e:
            self.logger.error(f"Error loading YAML file {file_path}: {str(e)}")
            return {}
    
    def save_yaml_file(self, file_path: str, data: Dict[str, Any]) -> bool:
        """
        Save data to YAML file
        
        Args:
            file_path: Path to the YAML file
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
                self.logger.info(f"Saved YAML data to {file_path}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving YAML file {file_path}: {str(e)}")
            return False
    
    def get_template(self, service: str, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a template for a service
        
        Args:
            service: Service name
            template_name: Template name
            
        Returns:
            Template data or None if not found
        """
        try:
            template_path = os.path.join(self.templates_dir, service, f"{template_name}.yaml")
            
            if not os.path.exists(template_path):
                self.logger.warning(f"Template {template_name} not found for service {service}")
                return None
            
            return self.load_yaml_file(template_path)
        except Exception as e:
            self.logger.error(f"Error loading template {template_name} for service {service}: {str(e)}")
            return None
    
    def get_available_templates(self, service: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available templates
        
        Args:
            service: Optional service to filter templates
            
        Returns:
            Dictionary mapping service to list of templates
        """
        templates: Dict[str, List[Dict[str, Any]]] = {}
        
        try:
            # If service is specified, only look in that directory
            if service:
                service_dir = os.path.join(self.templates_dir, service)
                if os.path.exists(service_dir) and os.path.isdir(service_dir):
                    templates[service] = self._get_templates_in_dir(service_dir)
            else:
                # Look in all service directories
                for item in os.listdir(self.templates_dir):
                    service_dir = os.path.join(self.templates_dir, item)
                    if os.path.isdir(service_dir):
                        service_templates = self._get_templates_in_dir(service_dir)
                        if service_templates:
                            templates[item] = service_templates
        except Exception as e:
            self.logger.error(f"Error getting available templates: {str(e)}")
        
        return templates
    
    def _get_templates_in_dir(self, directory: str) -> List[Dict[str, Any]]:
        """
        Get templates in a directory
        
        Args:
            directory: Directory to search for templates
            
        Returns:
            List of template metadata
        """
        templates = []
        
        for filename in os.listdir(directory):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                template_path = os.path.join(directory, filename)
                try:
                    # Load the template
                    template_data = self.load_yaml_file(template_path)
                    
                    # Extract template metadata
                    template_name = os.path.splitext(filename)[0]
                    template_metadata = {
                        "name": template_name,
                        "description": template_data.get("description", ""),
                        "path": template_path
                    }
                    
                    templates.append(template_metadata)
                except Exception as e:
                    self.logger.error(f"Error loading template {filename}: {str(e)}")
        
        return templates
    
    def create_template_from_resources(
        self,
        name: str,
        description: str,
        resources: List[Dict[str, Any]],
        output_path: str
    ) -> Optional[str]:
        """
        Create a template from existing resources
        
        Args:
            name: Name of the template
            description: Description of the template
            resources: List of resource details
            output_path: Directory to save the template
            
        Returns:
            Path to the created template, or None if failed
        """
        try:
            # Group resources by service
            resources_by_service: Dict[str, List[Dict[str, Any]]] = {}
            
            for resource in resources:
                service = resource["service"]
                if service not in resources_by_service:
                    resources_by_service[service] = []
                
                resources_by_service[service].append(resource)
            
            # Create a template for each service
            template_paths = []
            
            for service, service_resources in resources_by_service.items():
                # Create service directory if it doesn't exist
                service_dir = os.path.join(output_path, service)
                os.makedirs(service_dir, exist_ok=True)
                
                # Create the template
                template_data = {
                    "name": name,
                    "description": description,
                    "resources": [resource["details"] for resource in service_resources]
                }
                
                # Save the template
                template_path = os.path.join(service_dir, f"{name}.yaml")
                if self.save_yaml_file(template_path, template_data):
                    template_paths.append(template_path)
            
            if not template_paths:
                self.logger.error(f"Failed to create any templates")
                return None
            
            return template_paths[0]  # Return the first template path
        except Exception as e:
            self.logger.error(f"Error creating template from resources: {str(e)}")
            return None 