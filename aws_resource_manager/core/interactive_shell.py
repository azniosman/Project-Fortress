#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Shell for AWS Resource Manager

This module provides an interactive shell interface for the AWS Resource Manager.
"""

import os
import sys
import shlex
import logging
from typing import List, Dict, Any, Optional, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Setup logger
logger = logging.getLogger(__name__)

class InteractiveShell:
    """
    Interactive shell for AWS Resource Manager.
    
    This class provides an interactive shell interface that allows users
    to execute AWS Resource Manager commands interactively.
    """
    
    def __init__(self, engine):
        """
        Initialize the interactive shell.
        
        Args:
            engine: The ResourceEngine instance to use for executing commands
        """
        self.engine = engine
        self.console = Console()
        
        # Command history file in user's home directory
        history_file = os.path.expanduser('~/.aws_resource_manager_history')
        
        # Create prompt session with history
        self.session = PromptSession(
            history=FileHistory(history_file),
            auto_suggest=AutoSuggestFromHistory()
        )
        
        # Define available commands
        self.commands = {
            'create': self.cmd_create,
            'list': self.cmd_list,
            'delete': self.cmd_delete,
            'update': self.cmd_update,
            'export': self.cmd_export,
            'templates': self.cmd_list_templates,
            'batch': self.cmd_batch_create,
            'compliance': self.cmd_check_compliance,
            'help': self.cmd_help,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit
        }
        
        # Create command completer
        self.completer = WordCompleter(list(self.commands.keys()) + ['help'], ignore_case=True)
        
        # Define styles
        self.style = Style.from_dict({
            'prompt': 'ansicyan bold',
        })

    def start(self):
        """
        Start the interactive shell.
        
        This method starts the interactive shell and processes user commands
        until the user exits.
        """
        running = True
        
        while running:
            try:
                # Display prompt and get user input
                user_input = self.session.prompt(
                    HTML('<ansicyan><b>aws-manager></b></ansicyan> '),
                    completer=self.completer,
                    style=self.style
                ).strip()
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Process the command
                running = self.process_command(user_input)
                
            except KeyboardInterrupt:
                # Handle Ctrl+C
                self.console.print("\n[yellow]Operation cancelled[/yellow]")
                continue
            except EOFError:
                # Handle Ctrl+D
                self.console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                logger.exception("Error in shell")
                self.console.print(f"[bold red]Error: {str(e)}[/bold red]")
    
    def process_command(self, user_input: str) -> bool:
        """
        Process a user command.
        
        Args:
            user_input: The command entered by the user
            
        Returns:
            bool: True to continue running, False to exit
        """
        # Parse the command and arguments
        parts = shlex.split(user_input)
        command = parts[0].lower()
        args = parts[1:]
        
        # Check if it's a valid command
        if command in self.commands:
            try:
                # Execute the command
                return self.commands[command](args)
            except Exception as e:
                logger.exception(f"Error executing command: {command}")
                self.console.print(f"[bold red]Error executing command: {str(e)}[/bold red]")
                return True
        else:
            self.console.print(f"[bold red]Unknown command: {command}[/bold red]")
            self.console.print("Type 'help' to see available commands")
            return True
    
    def cmd_help(self, args: List[str]) -> bool:
        """
        Display help information.
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if args and args[0] in self.commands:
            # Display help for specific command
            command = args[0]
            self.console.print(f"[bold]Help for command: {command}[/bold]")
            # Get the docstring from the command function
            doc = self.commands[command].__doc__ or "No help available"
            self.console.print(doc)
        else:
            # Display general help
            self.console.print("[bold blue]Available Commands:[/bold blue]")
            
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Command")
            table.add_column("Description")
            
            table.add_row("create", "Create AWS resources")
            table.add_row("list", "List AWS resources")
            table.add_row("delete", "Delete AWS resources")
            table.add_row("update", "Update AWS resources")
            table.add_row("export", "Export resources as Infrastructure as Code")
            table.add_row("templates", "List available templates")
            table.add_row("batch", "Create resources from a YAML file")
            table.add_row("compliance", "Check resources for compliance")
            table.add_row("help", "Display this help message")
            table.add_row("exit/quit", "Exit the shell")
            
            self.console.print(table)
            
            self.console.print("\n[bold yellow]For help on a specific command, type: help <command>[/bold yellow]")
        
        return True
    
    def cmd_exit(self, args: List[str]) -> bool:
        """
        Exit the shell.
        
        Args:
            args: Command arguments
            
        Returns:
            bool: False to exit
        """
        self.console.print("[yellow]Exiting AWS Resource Manager...[/yellow]")
        return False
    
    def cmd_create(self, args: List[str]) -> bool:
        """
        Create AWS resources.
        
        Usage: create <service> [--name <resource_name>] [--template <template>] [--guided] [--dry-run]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if not args:
            self.console.print("[bold red]Error: Service name required[/bold red]")
            self.console.print("Usage: create <service> [--name <resource_name>] [--template <template>] [--guided] [--dry-run]")
            return True
        
        # Parse arguments
        service = args[0]
        resource_name = None
        template = None
        guided = False
        dry_run = False
        
        i = 1
        while i < len(args):
            if args[i] == "--name" and i + 1 < len(args):
                resource_name = args[i + 1]
                i += 2
            elif args[i] == "--template" and i + 1 < len(args):
                template = args[i + 1]
                i += 2
            elif args[i] == "--guided":
                guided = True
                i += 1
            elif args[i] == "--dry-run":
                dry_run = True
                i += 1
            else:
                i += 1
        
        # Execute the create operation
        self.console.print(f"[bold blue]Creating {service} resource...[/bold blue]")
        
        try:
            result = self.engine.create_resource(
                service=service,
                resource_name=resource_name,
                template_name=template,
                guided=guided,
                dry_run=dry_run,
                skip_dependency_check=False
            )
            
            if result.success:
                self.console.print(f"[bold green]Successfully created {service} resource:[/bold green]")
                self.console.print(result.output)
            else:
                self.console.print(f"[bold red]Failed to create {service} resource:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error creating resource")
            self.console.print(f"[bold red]Error creating resource: {str(e)}[/bold red]")
        
        return True
    
    def cmd_list(self, args: List[str]) -> bool:
        """
        List AWS resources.
        
        Usage: list <service> [--output <format>] [--filter <filter_expr>]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if not args:
            self.console.print("[bold red]Error: Service name required[/bold red]")
            self.console.print("Usage: list <service> [--output <format>] [--filter <filter_expr>]")
            return True
        
        # Parse arguments
        service = args[0]
        output_format = "rich"
        filter_expr = None
        
        i = 1
        while i < len(args):
            if args[i] == "--output" and i + 1 < len(args):
                output_format = args[i + 1]
                i += 2
            elif args[i] == "--filter" and i + 1 < len(args):
                filter_expr = args[i + 1]
                i += 2
            else:
                i += 1
        
        # Execute the list operation
        self.console.print(f"[bold blue]Listing {service} resources...[/bold blue]")
        
        try:
            result = self.engine.list_resources(
                service=service,
                output_format=output_format,
                filter_expr=filter_expr
            )
            
            if result.success:
                self.console.print(f"[bold green]{service.upper()} Resources:[/bold green]")
                self.console.print(result.output)
            else:
                self.console.print(f"[bold red]Failed to list {service} resources:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error listing resources")
            self.console.print(f"[bold red]Error listing resources: {str(e)}[/bold red]")
        
        return True
    
    def cmd_delete(self, args: List[str]) -> bool:
        """
        Delete AWS resources.
        
        Usage: delete <service> <resource_id> [--force] [--dry-run]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if len(args) < 2:
            self.console.print("[bold red]Error: Service name and resource ID required[/bold red]")
            self.console.print("Usage: delete <service> <resource_id> [--force] [--dry-run]")
            return True
        
        # Parse arguments
        service = args[0]
        resource_id = args[1]
        force = False
        dry_run = False
        
        i = 2
        while i < len(args):
            if args[i] == "--force":
                force = True
                i += 1
            elif args[i] == "--dry-run":
                dry_run = True
                i += 1
            else:
                i += 1
        
        # Ask for confirmation if not forced
        if not force:
            from prompt_toolkit.shortcuts import confirm
            confirmed = confirm(f"Are you sure you want to delete the {service} resource with ID {resource_id}?")
            if not confirmed:
                self.console.print("[yellow]Operation cancelled by user[/yellow]")
                return True
        
        # Execute the delete operation
        self.console.print(f"[bold blue]Deleting {service} resource...[/bold blue]")
        
        try:
            result = self.engine.delete_resource(
                service=service,
                resource_id=resource_id,
                dry_run=dry_run,
                skip_dependency_check=False
            )
            
            if result.success:
                self.console.print(f"[bold green]Successfully deleted {service} resource:[/bold green]")
                self.console.print(result.output)
            else:
                self.console.print(f"[bold red]Failed to delete {service} resource:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error deleting resource")
            self.console.print(f"[bold red]Error deleting resource: {str(e)}[/bold red]")
        
        return True
    
    def cmd_update(self, args: List[str]) -> bool:
        """
        Update AWS resources.
        
        Usage: update <service> <resource_id> [--param key=value]... [--guided] [--dry-run]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if len(args) < 2:
            self.console.print("[bold red]Error: Service name and resource ID required[/bold red]")
            self.console.print("Usage: update <service> <resource_id> [--param key=value]... [--guided] [--dry-run]")
            return True
        
        # Parse arguments
        service = args[0]
        resource_id = args[1]
        params = {}
        guided = False
        dry_run = False
        
        i = 2
        while i < len(args):
            if args[i] == "--param" and i + 1 < len(args):
                param = args[i + 1]
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
                i += 2
            elif args[i] == "--guided":
                guided = True
                i += 1
            elif args[i] == "--dry-run":
                dry_run = True
                i += 1
            else:
                i += 1
        
        # Execute the update operation
        self.console.print(f"[bold blue]Updating {service} resource...[/bold blue]")
        
        try:
            result = self.engine.update_resource(
                service=service,
                resource_id=resource_id,
                parameters=params,
                guided=guided,
                dry_run=dry_run
            )
            
            if result.success:
                self.console.print(f"[bold green]Successfully updated {service} resource:[/bold green]")
                self.console.print(result.output)
            else:
                self.console.print(f"[bold red]Failed to update {service} resource:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error updating resource")
            self.console.print(f"[bold red]Error updating resource: {str(e)}[/bold red]")
        
        return True
    
    def cmd_export(self, args: List[str]) -> bool:
        """
        Export AWS resources as Infrastructure as Code.
        
        Usage: export [--format <format>] [--output <path>] [--resource <id>]... [--region <region>]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        # Parse arguments
        export_format = "terraform"
        output_path = "."
        resource_ids = []
        region = None
        
        i = 0
        while i < len(args):
            if args[i] == "--format" and i + 1 < len(args):
                export_format = args[i + 1]
                i += 2
            elif args[i] == "--output" and i + 1 < len(args):
                output_path = args[i + 1]
                i += 2
            elif args[i] == "--resource" and i + 1 < len(args):
                resource_ids.append(args[i + 1])
                i += 2
            elif args[i] == "--region" and i + 1 < len(args):
                region = args[i + 1]
                i += 2
            else:
                i += 1
        
        # Execute the export operation
        self.console.print(f"[bold blue]Exporting resources as {export_format}...[/bold blue]")
        
        try:
            result = self.engine.export_resources(
                export_format=export_format,
                output_path=output_path,
                resource_ids=resource_ids,
                region=region
            )
            
            if result.success:
                self.console.print(f"[bold green]Successfully exported resources:[/bold green]")
                self.console.print(f"Output: {result.output}")
            else:
                self.console.print(f"[bold red]Failed to export resources:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error exporting resources")
            self.console.print(f"[bold red]Error exporting resources: {str(e)}[/bold red]")
        
        return True
    
    def cmd_list_templates(self, args: List[str]) -> bool:
        """
        List available templates for resource creation.
        
        Usage: templates [--service <service>]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        # Parse arguments
        service = None
        
        i = 0
        while i < len(args):
            if args[i] == "--service" and i + 1 < len(args):
                service = args[i + 1]
                i += 2
            else:
                i += 1
        
        # Execute the list templates operation
        self.console.print("[bold blue]Loading templates...[/bold blue]")
        
        try:
            templates = self.engine.get_templates(service)
            
            if templates:
                self.console.print("[bold green]Available Templates:[/bold green]")
                for category, template_list in templates.items():
                    self.console.print(f"\n[bold cyan]{category.upper()}[/bold cyan]")
                    for template in template_list:
                        self.console.print(f"  [yellow]{template['name']}[/yellow]: {template['description']}")
            else:
                self.console.print("[yellow]No templates found[/yellow]")
        except Exception as e:
            logger.exception("Error listing templates")
            self.console.print(f"[bold red]Error listing templates: {str(e)}[/bold red]")
        
        return True
    
    def cmd_batch_create(self, args: List[str]) -> bool:
        """
        Create multiple AWS resources from a YAML file.
        
        Usage: batch <file> [--dry-run] [--ignore-errors]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if not args:
            self.console.print("[bold red]Error: YAML file path required[/bold red]")
            self.console.print("Usage: batch <file> [--dry-run] [--ignore-errors]")
            return True
        
        # Parse arguments
        file_path = args[0]
        dry_run = False
        ignore_errors = False
        
        i = 1
        while i < len(args):
            if args[i] == "--dry-run":
                dry_run = True
                i += 1
            elif args[i] == "--ignore-errors":
                ignore_errors = True
                i += 1
            else:
                i += 1
        
        # Execute the batch create operation
        self.console.print(f"[bold blue]Creating resources from {file_path}...[/bold blue]")
        
        try:
            result = self.engine.batch_create_resources(
                file_path=file_path,
                dry_run=dry_run,
                ignore_errors=ignore_errors
            )
            
            if result.success:
                self.console.print(f"[bold green]Successfully created resources:[/bold green]")
                self.console.print(result.output)
            else:
                self.console.print(f"[bold red]Failed to create resources:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error in batch creation")
            self.console.print(f"[bold red]Error in batch creation: {str(e)}[/bold red]")
        
        return True
    
    def cmd_check_compliance(self, args: List[str]) -> bool:
        """
        Check AWS resources for compliance with security standards.
        
        Usage: compliance <service> [--type <resource_type>] [--id <resource_id>] [--standard <standard>] [--output <format>] [--report <file>] [--severity <level>]
        
        Args:
            args: Command arguments
            
        Returns:
            bool: True to continue running
        """
        if not args:
            self.console.print("[bold red]Error: Service name required[/bold red]")
            self.console.print("Usage: compliance <service> [--type <resource_type>] [--id <resource_id>] [--standard <standard>] [--output <format>] [--report <file>] [--severity <level>]")
            return True
        
        # Parse arguments
        service = args[0]
        resource_type = None
        resource_id = None
        standard = "pci-dss"
        output_format = "rich"
        report_file = None
        severity_threshold = "warning"
        
        i = 1
        while i < len(args):
            if args[i] == "--type" and i + 1 < len(args):
                resource_type = args[i + 1]
                i += 2
            elif args[i] == "--id" and i + 1 < len(args):
                resource_id = args[i + 1]
                i += 2
            elif args[i] == "--standard" and i + 1 < len(args):
                standard = args[i + 1]
                i += 2
            elif args[i] == "--output" and i + 1 < len(args):
                output_format = args[i + 1]
                i += 2
            elif args[i] == "--report" and i + 1 < len(args):
                report_file = args[i + 1]
                i += 2
            elif args[i] == "--severity" and i + 1 < len(args):
                severity_threshold = args[i + 1]
                i += 2
            else:
                i += 1
        
        # Prepare parameters for the operation
        params = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "standard": standard,
            "severity_threshold": severity_threshold
        }
        
        # Execute the check_compliance operation
        self.console.print(f"[bold blue]Checking {service} compliance against {standard}...[/bold blue]")
        
        try:
            result = self.engine.execute_operation(
                service=service,
                operation="check_compliance",
                **params
            )
            
            if result.success:
                # Display results based on output format
                if output_format == "rich":
                    self._display_compliance_results(result.output, service, standard)
                elif output_format == "json":
                    import json
                    self.console.print(json.dumps(result.output, indent=2))
                elif output_format == "yaml":
                    import yaml
                    self.console.print(yaml.dump(result.output))
                
                # Save report if requested
                if report_file:
                    self._save_compliance_report(result.output, report_file, output_format)
                    self.console.print(f"[green]Compliance report saved to {report_file}[/green]")
            else:
                self.console.print(f"[bold red]Failed to check {service} compliance:[/bold red]")
                self.console.print(f"[red]{result.error_message}[/red]")
        except Exception as e:
            logger.exception("Error checking compliance")
            self.console.print(f"[bold red]Error checking compliance: {str(e)}[/bold red]")
        
        return True
    
    def _display_compliance_results(self, results: Dict[str, Any], service: str, standard: str) -> None:
        """
        Display compliance results in a rich format.
        
        Args:
            results: The compliance check results
            service: The service that was checked
            standard: The compliance standard used
        """
        from rich.table import Table
        
        self.console.print(f"[bold blue]Compliance Report: {service.upper()} against {standard.upper()}[/bold blue]")
        
        # Generic display for any service
        if isinstance(results, dict):
            for category, items in results.items():
                self.console.print(f"\n[bold]{category.replace('_', ' ').title()}:[/bold]")
                
                if isinstance(items, dict):
                    table = Table(show_header=True, header_style="bold")
                    
                    # Try to determine columns based on content
                    if "compliant" in items:
                        table.add_column("Status")
                        
                        if items["compliant"]:
                            table.add_row("[green]Compliant[/green]")
                        else:
                            table.add_row("[red]Non-compliant[/red]")
                            
                            # Display issues if present
                            if "issues" in items and isinstance(items["issues"], list):
                                for issue in items["issues"]:
                                    self.console.print(f"  - [red]{issue}[/red]")
                    else:
                        # Generic table for unknown structure
                        table.add_column("Key")
                        table.add_column("Value")
                        
                        for key, value in items.items():
                            if not isinstance(value, (dict, list)):
                                table.add_row(key, str(value))
                    
                    self.console.print(table)
                elif isinstance(items, list):
                    for item in items:
                        if isinstance(item, str):
                            self.console.print(f"  - {item}")
                        else:
                            self.console.print(f"  - {str(item)}")
                else:
                    self.console.print(f"  {str(items)}")
        else:
            # Fallback for non-dict results
            self.console.print(str(results))
    
    def _save_compliance_report(self, results: Dict[str, Any], filename: str, format: str) -> None:
        """
        Save compliance results to a file.
        
        Args:
            results: The compliance check results
            filename: The file to save to
            format: The output format
        """
        with open(filename, 'w') as f:
            if format == "json":
                import json
                json.dump(results, f, indent=2)
            elif format == "yaml":
                import yaml
                yaml.dump(results, f)
            else:
                # Default to pretty text format
                from rich.console import Console
                file_console = Console(file=f, width=100)
                file_console.print(results)
