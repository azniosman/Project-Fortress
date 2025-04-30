#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Resource Engine - Core module for orchestrating AWS resource operations

This module provides the central orchestration for all AWS resource operations,
including creation, updating, deletion, listing, and exporting.
"""

import os
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass

from core.plugin_manager import PluginManager
from core.config_manager import ConfigManager
from core.dependency_resolver import DependencyResolver
from utils.logger import setup_logger

@dataclass
class OperationResult:
    """Class to represent the result of an operation"""
    success: bool
    output: Any = None
    error_message: str = ""

class ResourceEngine:
    """
    Central orchestration engine for AWS resource operations
    
    This class coordinates all interactions between different components of the
    system, including the plugin manager, configuration manager, and dependency resolver.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        plugin_manager: PluginManager,
        dependency_resolver: DependencyResolver
    ):
        """
        Initialize the ResourceEngine
        
        Args:
            config_manager: The configuration manager
            plugin_manager: The plugin manager
            dependency_resolver: The dependency resolver
        """
        self.config_manager = config_manager
        self.plugin_manager = plugin_manager
        self.dependency_resolver = dependency_resolver
        self.logger = setup_logger(__name__)
    
    def create_resource(
        self,
        service: str,
        resource_name: Optional[str] = None,
        template_name: Optional[str] = None,
        guided: bool = False,
        dry_run: bool = False,
        skip_dependency_check: bool = False
    ) -> OperationResult:
        """
        Create an AWS resource
        
        Args:
            service: The AWS service (e.g., ec2, s3, rds)
            resource_name: Optional name for the resource
            template_name: Optional template to use for creation
            guided: Whether to use guided wizard mode
            dry_run: Whether to validate without creating
            skip_dependency_check: Whether to skip dependency validation
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Creating {service} resource")
            
            # Get the service module
            service_module = self.plugin_manager.get_service_module(service)
            if not service_module:
                return OperationResult(
                    success=False,
                    error_message=f"Service module '{service}' not found"
                )
            
            # Load template if provided
            template_config = None
            if template_name:
                template_config = self.config_manager.get_template(service, template_name)
                if not template_config:
                    return OperationResult(
                        success=False,
                        error_message=f"Template '{template_name}' not found for service '{service}'"
                    )
            
            # Check dependencies if needed
            if not skip_dependency_check:
                dependency_issues = self.dependency_resolver.check_dependencies(service, template_config)
                if dependency_issues:
                    return OperationResult(
                        success=False,
                        error_message=f"Dependency issues: {', '.join(dependency_issues)}"
                    )
            
            # Perform the creation
            creation_params = {
                "resource_name": resource_name,
                "template_config": template_config,
                "guided": guided,
                "dry_run": dry_run
            }
            
            result = service_module.execute_operation("create", **creation_params)
            
            if result.get("success"):
                self.logger.info(f"Successfully created {service} resource")
                return OperationResult(
                    success=True,
                    output=result.get("output")
                )
            else:
                self.logger.error(f"Failed to create {service} resource: {result.get('error')}")
                return OperationResult(
                    success=False,
                    error_message=result.get("error")
                )
                
        except Exception as e:
            self.logger.exception(f"Error creating {service} resource")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def list_resources(
        self,
        service: str,
        output_format: str = "rich",
        filter_expr: Optional[str] = None
    ) -> OperationResult:
        """
        List AWS resources
        
        Args:
            service: The AWS service (e.g., ec2, s3, rds)
            output_format: Output format (rich, json, yaml)
            filter_expr: Optional filter expression
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Listing {service} resources")
            
            # Get the service module
            service_module = self.plugin_manager.get_service_module(service)
            if not service_module:
                return OperationResult(
                    success=False,
                    error_message=f"Service module '{service}' not found"
                )
            
            # Perform the listing
            list_params = {
                "output_format": output_format,
                "filter_expr": filter_expr
            }
            
            result = service_module.execute_operation("list", **list_params)
            
            if result.get("success"):
                self.logger.info(f"Successfully listed {service} resources")
                return OperationResult(
                    success=True,
                    output=result.get("output")
                )
            else:
                self.logger.error(f"Failed to list {service} resources: {result.get('error')}")
                return OperationResult(
                    success=False,
                    error_message=result.get("error")
                )
                
        except Exception as e:
            self.logger.exception(f"Error listing {service} resources")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def update_resource(
        self,
        service: str,
        resource_id: str,
        parameters: Dict[str, Any],
        guided: bool = False,
        dry_run: bool = False
    ) -> OperationResult:
        """
        Update an AWS resource
        
        Args:
            service: The AWS service (e.g., ec2, s3, rds)
            resource_id: The ID of the resource to update
            parameters: Parameters to update
            guided: Whether to use guided wizard mode
            dry_run: Whether to validate without updating
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Updating {service} resource {resource_id}")
            
            # Get the service module
            service_module = self.plugin_manager.get_service_module(service)
            if not service_module:
                return OperationResult(
                    success=False,
                    error_message=f"Service module '{service}' not found"
                )
            
            # Perform the update
            update_params = {
                "resource_id": resource_id,
                "parameters": parameters,
                "guided": guided,
                "dry_run": dry_run
            }
            
            result = service_module.execute_operation("update", **update_params)
            
            if result.get("success"):
                self.logger.info(f"Successfully updated {service} resource {resource_id}")
                return OperationResult(
                    success=True,
                    output=result.get("output")
                )
            else:
                self.logger.error(f"Failed to update {service} resource {resource_id}: {result.get('error')}")
                return OperationResult(
                    success=False,
                    error_message=result.get("error")
                )
                
        except Exception as e:
            self.logger.exception(f"Error updating {service} resource {resource_id}")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def delete_resource(
        self,
        service: str,
        resource_id: str,
        dry_run: bool = False,
        skip_dependency_check: bool = False
    ) -> OperationResult:
        """
        Delete an AWS resource
        
        Args:
            service: The AWS service (e.g., ec2, s3, rds)
            resource_id: The ID of the resource to delete
            dry_run: Whether to validate without deleting
            skip_dependency_check: Whether to skip dependency validation
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Deleting {service} resource {resource_id}")
            
            # Get the service module
            service_module = self.plugin_manager.get_service_module(service)
            if not service_module:
                return OperationResult(
                    success=False,
                    error_message=f"Service module '{service}' not found"
                )
            
            # Check for dependent resources if needed
            if not skip_dependency_check:
                dependents = self.dependency_resolver.get_dependent_resources(service, resource_id)
                if dependents:
                    dependent_list = ", ".join([f"{d['service']}:{d['id']}" for d in dependents])
                    return OperationResult(
                        success=False,
                        error_message=f"Cannot delete: resource has dependents: {dependent_list}"
                    )
            
            # Perform the deletion
            delete_params = {
                "resource_id": resource_id,
                "dry_run": dry_run
            }
            
            result = service_module.execute_operation("delete", **delete_params)
            
            if result.get("success"):
                self.logger.info(f"Successfully deleted {service} resource {resource_id}")
                return OperationResult(
                    success=True,
                    output=result.get("output")
                )
            else:
                self.logger.error(f"Failed to delete {service} resource {resource_id}: {result.get('error')}")
                return OperationResult(
                    success=False,
                    error_message=result.get("error")
                )
                
        except Exception as e:
            self.logger.exception(f"Error deleting {service} resource {resource_id}")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def batch_create_resources(
        self,
        file_path: str,
        dry_run: bool = False,
        ignore_errors: bool = False
    ) -> OperationResult:
        """
        Create multiple AWS resources from a YAML file
        
        Args:
            file_path: Path to the YAML file with resource definitions
            dry_run: Whether to validate without creating
            ignore_errors: Whether to continue on error
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Batch creating resources from {file_path}")
            
            # Load the batch configuration
            batch_config = self.config_manager.load_yaml_file(file_path)
            if not batch_config:
                return OperationResult(
                    success=False,
                    error_message=f"Failed to load batch configuration from {file_path}"
                )
            
            # Sort resources by dependencies
            resources = batch_config.get("resources", [])
            sorted_resources = self.dependency_resolver.sort_resources_by_dependencies(resources)
            
            # Create resources in order
            results = []
            failures = []
            
            for resource in sorted_resources:
                service = resource.get("service")
                resource_name = resource.get("name")
                
                resource_result = self.create_resource(
                    service=service,
                    resource_name=resource_name,
                    guided=False,
                    dry_run=dry_run,
                    skip_dependency_check=True  # Already handled by sorting
                )
                
                results.append({
                    "service": service,
                    "name": resource_name,
                    "success": resource_result.success,
                    "output": resource_result.output if resource_result.success else resource_result.error_message
                })
                
                if not resource_result.success and not ignore_errors:
                    failures.append(f"{service} resource '{resource_name}': {resource_result.error_message}")
                    break
            
            if failures and not ignore_errors:
                return OperationResult(
                    success=False,
                    error_message=f"Batch creation failed: {', '.join(failures)}",
                    output=results
                )
            
            return OperationResult(
                success=True,
                output=results
            )
                
        except Exception as e:
            self.logger.exception(f"Error in batch resource creation")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def export_resources(
        self,
        export_format: str,
        output_path: str,
        resource_ids: Optional[List[str]] = None,
        region: Optional[str] = None
    ) -> OperationResult:
        """
        Export AWS resources as Infrastructure as Code
        
        Args:
            export_format: Export format (terraform, cloudformation, cdk)
            output_path: Output directory or file
            resource_ids: Optional list of resource IDs to export
            region: Optional AWS region of resources
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Exporting resources as {export_format}")
            
            # Get all service modules that support exporting
            export_modules = [
                module for module in self.plugin_manager.get_all_service_modules()
                if "export" in module.get_operations()
            ]
            
            if not export_modules:
                return OperationResult(
                    success=False,
                    error_message=f"No service modules support exporting to {export_format}"
                )
            
            export_params = {
                "export_format": export_format,
                "output_path": output_path,
                "resource_ids": resource_ids,
                "region": region
            }
            
            # Export resources from each module
            export_results = {}
            for module in export_modules:
                service = module.get_service_name()
                result = module.execute_operation("export", **export_params)
                export_results[service] = result
            
            # Generate summary
            successful_services = [
                service for service, result in export_results.items() 
                if result.get("success")
            ]
            
            failed_services = {
                service: result.get("error") 
                for service, result in export_results.items() 
                if not result.get("success")
            }
            
            if failed_services:
                failures_str = ", ".join([f"{service}: {error}" for service, error in failed_services.items()])
                return OperationResult(
                    success=False,
                    error_message=f"Export partially failed: {failures_str}",
                    output={
                        "successful_services": successful_services,
                        "failed_services": failed_services,
                        "output_path": output_path
                    }
                )
            
            return OperationResult(
                success=True,
                output={
                    "successful_services": successful_services,
                    "output_path": output_path
                }
            )
                
        except Exception as e:
            self.logger.exception(f"Error exporting resources")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def get_templates(self, service: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available templates for resource creation
        
        Args:
            service: Optional service to filter templates
            
        Returns:
            Dictionary of templates organized by service
        """
        try:
            return self.config_manager.get_available_templates(service)
        except Exception as e:
            self.logger.exception(f"Error getting templates")
            return {}
    
    def create_template(
        self,
        name: str,
        description: str,
        resource_ids: List[str],
        output_path: str
    ) -> OperationResult:
        """
        Create a new template from existing resources
        
        Args:
            name: Name of the template
            description: Description of the template
            resource_ids: List of resource IDs to include in the template
            output_path: Directory to save the template
            
        Returns:
            OperationResult with success/failure and details
        """
        try:
            self.logger.info(f"Creating template '{name}' from resources {resource_ids}")
            
            # Parse resource IDs
            parsed_resources = []
            for resource_id in resource_ids:
                # Expects format "service:id" (e.g., "ec2:i-12345")
                if ":" not in resource_id:
                    return OperationResult(
                        success=False,
                        error_message=f"Invalid resource ID format: {resource_id}. Expected 'service:id'"
                    )
                
                service, id = resource_id.split(":", 1)
                
                # Get the service module
                service_module = self.plugin_manager.get_service_module(service)
                if not service_module:
                    return OperationResult(
                        success=False,
                        error_message=f"Service module '{service}' not found for resource {resource_id}"
                    )
                
                # Get resource details
                result = service_module.execute_operation("describe", resource_id=id)
                if not result.get("success"):
                    return OperationResult(
                        success=False,
                        error_message=f"Failed to get details for {resource_id}: {result.get('error')}"
                    )
                
                parsed_resources.append({
                    "service": service,
                    "id": id,
                    "details": result.get("output")
                })
            
            # Create template from resources
            template_path = self.config_manager.create_template_from_resources(
                name=name,
                description=description,
                resources=parsed_resources,
                output_path=output_path
            )
            
            if not template_path:
                return OperationResult(
                    success=False,
                    error_message=f"Failed to create template '{name}'"
                )
            
            return OperationResult(
                success=True,
                output=template_path
            )
                
        except Exception as e:
            self.logger.exception(f"Error creating template")
            return OperationResult(
                success=False,
                error_message=str(e)
            )
    
    def check_permissions(self) -> List[str]:
        """
        Check AWS permissions for required operations
        
        Returns:
            List of permission issues (empty if all permissions are granted)
        """
        try:
            # Get all service modules
            service_modules = self.plugin_manager.get_all_service_modules()
            
            # Check permissions for each module
            permission_issues = []
            for module in service_modules:
                service = module.get_service_name()
                
                # Skip modules that don't have permission check
                if "check_permissions" not in module.get_operations():
                    continue
                
                # Check permissions
                result = module.execute_operation("check_permissions")
                if not result.get("success"):
                    permission_issues.append(f"{service}: {result.get('error')}")
            
            return permission_issues
                
        except Exception as e:
            self.logger.exception(f"Error checking permissions")
            return [f"Error checking permissions: {str(e)}"] 