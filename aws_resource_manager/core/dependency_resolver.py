#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Dependency Resolver - Manages dependencies between AWS resources

This module provides functionality to determine dependencies between AWS resources
and manage the creation and deletion order to ensure integrity.
"""

import logging
import networkx as nx
from typing import Dict, List, Any, Optional, Set, Tuple

from utils.logger import setup_logger

class DependencyResolver:
    """
    Manages dependencies between AWS resources
    
    This class is responsible for determining dependencies between AWS resources
    and managing the creation and deletion order to ensure integrity.
    """
    
    def __init__(self):
        """
        Initialize the dependency resolver
        """
        self.logger = setup_logger(__name__)
        self.dependency_rules = self._initialize_dependency_rules()
    
    def _initialize_dependency_rules(self) -> Dict[str, List[str]]:
        """
        Initialize dependency rules between services
        
        Returns:
            Dictionary mapping service to list of services it depends on
        """
        # Define the dependency rules for AWS services
        # Key: service, Value: list of services it depends on
        return {
            "vpc": [],
            "subnet": ["vpc"],
            "security_group": ["vpc"],
            "internet_gateway": ["vpc"],
            "nat_gateway": ["subnet", "internet_gateway"],
            "route_table": ["vpc"],
            "ec2": ["subnet", "security_group"],
            "rds": ["subnet", "security_group"],
            "elasticache": ["subnet", "security_group"],
            "elb": ["subnet", "security_group"],
            "lambda": ["security_group"],
            "ecs": ["vpc", "security_group"],
            "eks": ["vpc", "subnet", "security_group"],
            "s3": [],
            "dynamodb": [],
            "sqs": [],
            "sns": [],
            "iam": []
        }
    
    def check_dependencies(self, service: str, template: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Check if dependencies are met for a service
        
        Args:
            service: The service to check
            template: Optional template configuration
            
        Returns:
            List of dependency issues (empty if dependencies are met)
        """
        if service not in self.dependency_rules:
            self.logger.warning(f"No dependency rules defined for service {service}")
            return []
        
        dependency_issues = []
        required_services = self.dependency_rules.get(service, [])
        
        if not required_services:
            return []
        
        if template:
            # Check if template provides required dependencies
            for required_service in required_services:
                if required_service not in template.get("dependencies", {}):
                    dependency_issues.append(f"Missing dependency: {required_service}")
        else:
            # Indicate that dependencies are required
            dependency_issues = [
                f"Service {service} requires these dependencies: {', '.join(required_services)}"
            ]
        
        return dependency_issues
    
    def get_dependent_resources(self, service: str, resource_id: str) -> List[Dict[str, str]]:
        """
        Get resources that depend on a specific resource
        
        Args:
            service: The service of the resource
            resource_id: The ID of the resource
            
        Returns:
            List of resources that depend on the specified resource
        """
        # This is a simplified implementation
        # In a real system, you would query for actual dependencies
        return []
    
    def sort_resources_by_dependencies(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort resources by dependencies to determine creation order
        
        Args:
            resources: List of resource configurations
            
        Returns:
            Sorted list of resources in creation order
        """
        try:
            # Create a directed graph
            G = nx.DiGraph()
            
            # Add nodes for all resources
            for i, resource in enumerate(resources):
                G.add_node(i, resource=resource)
            
            # Add edges for dependencies
            for i, resource in enumerate(resources):
                service = resource.get("service")
                if service not in self.dependency_rules:
                    continue
                
                # Get dependencies for this service
                required_services = self.dependency_rules.get(service, [])
                
                if not required_services:
                    continue
                
                # Find resources that this resource depends on
                for j, other_resource in enumerate(resources):
                    other_service = other_resource.get("service")
                    if other_service in required_services:
                        # This resource depends on the other resource
                        G.add_edge(j, i)
            
            # Check for cycles
            if not nx.is_directed_acyclic_graph(G):
                self.logger.error("Dependency cycle detected in resources")
                # Break cycles by removing edges
                cycles = list(nx.simple_cycles(G))
                for cycle in cycles:
                    if cycle:
                        G.remove_edge(cycle[0], cycle[-1])
            
            # Perform topological sort to get creation order
            try:
                sorted_indices = list(nx.topological_sort(G))
                sorted_resources = [resources[i] for i in sorted_indices]
                return sorted_resources
            except nx.NetworkXUnfeasible:
                self.logger.error("Could not perform topological sort, returning original order")
                return resources
        
        except Exception as e:
            self.logger.exception(f"Error sorting resources by dependencies: {str(e)}")
            return resources
    
    def check_deletion_safety(self, service: str, resource_id: str) -> Tuple[bool, List[str]]:
        """
        Check if it's safe to delete a resource
        
        Args:
            service: The service of the resource
            resource_id: The ID of the resource
            
        Returns:
            Tuple of (safe_to_delete, reasons)
        """
        dependent_resources = self.get_dependent_resources(service, resource_id)
        
        if dependent_resources:
            reasons = [
                f"Resource is depended on by: {dep['service']}:{dep['id']}"
                for dep in dependent_resources
            ]
            return False, reasons
        
        return True, [] 