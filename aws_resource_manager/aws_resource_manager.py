#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AWS Resource Manager - Main Entry Point

This script provides a comprehensive, modular interface for managing AWS resources
through an interactive command-line interface.
"""

import os
import sys
import logging
import importlib.util
from typing import List, Dict, Any, Optional

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import typer
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    print("Required dependencies not found. Installing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed. Restarting script...")
    os.execv(sys.executable, ['python'] + sys.argv)

# Import core modules
from core.engine import ResourceEngine
from core.plugin_manager import PluginManager
from core.config_manager import ConfigManager
from core.dependency_resolver import DependencyResolver
from utils.validators import validate_aws_credentials
from utils.logger import setup_logger

# Initialize Typer app
app = typer.Typer(
    help="AWS Resource Manager - A tool for managing AWS resources",
    add_completion=True
)

# Initialize Rich console
console = Console()

# Initialize logger
logger = setup_logger(__name__)

def check_dependencies() -> bool:
    """
    Check if all required dependencies are installed.
    
    Returns:
        bool: True if all dependencies are installed, False otherwise
    """
    required_packages = [
        "boto3", "typer", "rich", "pyyaml", "pydantic", 
        "networkx", "prompt_toolkit", "cryptography"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        console.print(f"[bold red]Missing dependencies: {', '.join(missing_packages)}[/bold red]")
        return False
    
    return True

def check_aws_cli_config() -> bool:
    """
    Check if AWS CLI is configured properly.
    
    Returns:
        bool: True if AWS CLI is configured, False otherwise
    """
    return validate_aws_credentials()

def display_welcome_banner() -> None:
    """
    Display a welcome banner when the application starts.
    """
    welcome_text = """
    AWS Resource Manager

    A comprehensive tool for managing AWS resources
    through an interactive command-line interface.

    Type --help for available commands or 'q' to quit.
    """
    
    console.print(Panel(welcome_text, title="Welcome", border_style="blue"))

def initialize_app() -> ResourceEngine:
    """
    Initialize the application and its components.
    
    Returns:
        ResourceEngine: The initialized resource engine
    """
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Initialize plugin manager and load plugins
    plugin_manager = PluginManager(config_manager)
    plugin_manager.discover_plugins()
    
    # Initialize dependency resolver
    dependency_resolver = DependencyResolver()
    
    # Initialize resource engine
    engine = ResourceEngine(
        config_manager=config_manager,
        plugin_manager=plugin_manager,
        dependency_resolver=dependency_resolver
    )
    
    return engine

@app.callback()
def main(
    ctx: typer.Context,
    log_level: str = typer.Option("info", help="Logging level (debug, info, warning, error)"),
    config_file: Optional[str] = typer.Option(None, help="Path to custom config file"),
    profile: str = typer.Option("default", help="AWS profile to use"),
    region: Optional[str] = typer.Option(None, help="AWS region to use")
) -> None:
    """
    AWS Resource Manager - A tool for managing AWS resources
    """
    # Set log level
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logging.basicConfig(level=numeric_level, handlers=[RichHandler()])
    
    # Store context in state
    ctx.obj = {
        "log_level": log_level,
        "config_file": config_file,
        "profile": profile,
        "region": region
    }
    
    # Display welcome banner if no command is specified
    if ctx.invoked_subcommand is None:
        display_welcome_banner()

@app.command()
def create(
    ctx: typer.Context,
    service: str = typer.Argument(..., help="AWS service (e.g., ec2, s3, rds)"),
    resource_name: str = typer.Option(None, help="Name of the resource to create"),
    template: str = typer.Option(None, help="Template to use for resource creation"),
    guided: bool = typer.Option(False, help="Use guided wizard for resource creation"),
    dry_run: bool = typer.Option(False, help="Validate inputs without creating resources"),
    output_format: str = typer.Option("rich", help="Output format (rich, json, yaml)"),
    skip_dependency_check: bool = typer.Option(False, help="Skip dependency validation")
) -> None:
    """
    Create AWS resources
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Creating {service} resource...", total=None)
        
        try:
            result = engine.create_resource(
                service=service,
                resource_name=resource_name,
                template_name=template,
                guided=guided,
                dry_run=dry_run,
                skip_dependency_check=skip_dependency_check
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]Successfully created {service} resource:[/bold green]")
                console.print(result.output)
            else:
                console.print(f"[bold red]Failed to create {service} resource:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error creating resource")
            console.print(f"[bold red]Error creating resource: {str(e)}[/bold red]")

@app.command()
def list(
    ctx: typer.Context,
    service: str = typer.Argument(..., help="AWS service (e.g., ec2, s3, rds)"),
    output_format: str = typer.Option("rich", help="Output format (rich, json, yaml)"),
    filter: str = typer.Option(None, help="Filter resources (e.g., Name=value)")
) -> None:
    """
    List AWS resources
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Listing {service} resources...", total=None)
        
        try:
            result = engine.list_resources(
                service=service,
                output_format=output_format,
                filter_expr=filter
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]{service.upper()} Resources:[/bold green]")
                console.print(result.output)
            else:
                console.print(f"[bold red]Failed to list {service} resources:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error listing resources")
            console.print(f"[bold red]Error listing resources: {str(e)}[/bold red]")

@app.command()
def delete(
    ctx: typer.Context,
    service: str = typer.Argument(..., help="AWS service (e.g., ec2, s3, rds)"),
    resource_id: str = typer.Argument(..., help="ID of the resource to delete"),
    force: bool = typer.Option(False, help="Force deletion without confirmation"),
    dry_run: bool = typer.Option(False, help="Validate inputs without deleting resources"),
    skip_dependency_check: bool = typer.Option(False, help="Skip dependency validation")
) -> None:
    """
    Delete AWS resources
    """
    engine = initialize_app()
    
    if not force:
        confirmed = typer.confirm(f"Are you sure you want to delete the {service} resource with ID {resource_id}?")
        if not confirmed:
            console.print("[yellow]Operation cancelled by user[/yellow]")
            return
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Deleting {service} resource...", total=None)
        
        try:
            result = engine.delete_resource(
                service=service,
                resource_id=resource_id,
                dry_run=dry_run,
                skip_dependency_check=skip_dependency_check
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]Successfully deleted {service} resource:[/bold green]")
                console.print(result.output)
            else:
                console.print(f"[bold red]Failed to delete {service} resource:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error deleting resource")
            console.print(f"[bold red]Error deleting resource: {str(e)}[/bold red]")

@app.command()
def update(
    ctx: typer.Context,
    service: str = typer.Argument(..., help="AWS service (e.g., ec2, s3, rds)"),
    resource_id: str = typer.Argument(..., help="ID of the resource to update"),
    parameters: List[str] = typer.Option([], help="Parameters to update (key=value)"),
    guided: bool = typer.Option(False, help="Use guided wizard for resource update"),
    dry_run: bool = typer.Option(False, help="Validate inputs without updating resources")
) -> None:
    """
    Update AWS resources
    """
    engine = initialize_app()
    
    # Parse parameters
    param_dict = {}
    for param in parameters:
        key, value = param.split('=', 1)
        param_dict[key] = value
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Updating {service} resource...", total=None)
        
        try:
            result = engine.update_resource(
                service=service,
                resource_id=resource_id,
                parameters=param_dict,
                guided=guided,
                dry_run=dry_run
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]Successfully updated {service} resource:[/bold green]")
                console.print(result.output)
            else:
                console.print(f"[bold red]Failed to update {service} resource:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error updating resource")
            console.print(f"[bold red]Error updating resource: {str(e)}[/bold red]")

@app.command()
def batch_create(
    ctx: typer.Context,
    file: str = typer.Argument(..., help="YAML file containing resource definitions"),
    dry_run: bool = typer.Option(False, help="Validate inputs without creating resources"),
    ignore_errors: bool = typer.Option(False, help="Continue on error")
) -> None:
    """
    Create multiple AWS resources from a YAML file
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Creating resources from {file}...", total=None)
        
        try:
            result = engine.batch_create_resources(
                file_path=file,
                dry_run=dry_run,
                ignore_errors=ignore_errors
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]Successfully created resources:[/bold green]")
                console.print(result.output)
            else:
                console.print(f"[bold red]Failed to create resources:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error in batch creation")
            console.print(f"[bold red]Error in batch creation: {str(e)}[/bold red]")

@app.command()
def export(
    ctx: typer.Context,
    format: str = typer.Option("terraform", help="Export format (terraform, cloudformation, cdk)"),
    output: str = typer.Option(".", help="Output directory or file"),
    resources: List[str] = typer.Option([], help="Resource IDs to export (all if empty)"),
    region: Optional[str] = typer.Option(None, help="AWS region of resources")
) -> None:
    """
    Export AWS resources as Infrastructure as Code
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Exporting resources as {format}...", total=None)
        
        try:
            result = engine.export_resources(
                export_format=format,
                output_path=output,
                resource_ids=resources,
                region=region or ctx.obj.get("region")
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]Successfully exported resources:[/bold green]")
                console.print(f"Output: {result.output}")
            else:
                console.print(f"[bold red]Failed to export resources:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error exporting resources")
            console.print(f"[bold red]Error exporting resources: {str(e)}[/bold red]")

@app.command()
def doctor(ctx: typer.Context) -> None:
    """
    Run diagnostics to check for common issues
    """
    console.print("[bold blue]Running diagnostics...[/bold blue]")
    
    # Check dependencies
    console.print("Checking Python dependencies...")
    if check_dependencies():
        console.print("[green]✓ All required Python packages are installed[/green]")
    else:
        console.print("[red]✗ Some required Python packages are missing[/red]")
    
    # Check AWS CLI configuration
    console.print("Checking AWS CLI configuration...")
    if check_aws_cli_config():
        console.print("[green]✓ AWS CLI is properly configured[/green]")
    else:
        console.print("[red]✗ AWS CLI configuration issue detected[/red]")
        console.print("""
        Try running: aws configure
        Or set environment variables:
        - AWS_ACCESS_KEY_ID
        - AWS_SECRET_ACCESS_KEY
        - AWS_REGION
        """)
    
    # Check for plugin issues
    engine = initialize_app()
    console.print("Checking plugins...")
    plugin_issues = engine.plugin_manager.check_plugins()
    
    if not plugin_issues:
        console.print("[green]✓ All plugins are working correctly[/green]")
    else:
        console.print("[red]✗ Some plugin issues detected:[/red]")
        for issue in plugin_issues:
            console.print(f"  - {issue}")
    
    # Check AWS permissions
    console.print("Checking AWS permissions...")
    try:
        permission_issues = engine.check_permissions()
        if not permission_issues:
            console.print("[green]✓ AWS permissions check passed[/green]")
        else:
            console.print("[red]✗ AWS permission issues detected:[/red]")
            for issue in permission_issues:
                console.print(f"  - {issue}")
    except Exception as e:
        console.print(f"[red]✗ Error checking AWS permissions: {str(e)}[/red]")
    
    console.print("[bold blue]Diagnostics complete[/bold blue]")

@app.command()
def shell(ctx: typer.Context) -> None:
    """
    Start an interactive shell for managing AWS resources
    """
    from core.interactive_shell import InteractiveShell
    
    engine = initialize_app()
    shell = InteractiveShell(engine)
    
    display_welcome_banner()
    shell.start()

@app.command()
def list_templates(ctx: typer.Context, service: Optional[str] = typer.Option(None, help="Filter templates by service")) -> None:
    """
    List available templates for resource creation
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Loading templates...", total=None)
        
        try:
            templates = engine.get_templates(service)
            
            progress.update(task, completed=True)
            
            if templates:
                console.print("[bold green]Available Templates:[/bold green]")
                for category, template_list in templates.items():
                    console.print(f"\n[bold cyan]{category.upper()}[/bold cyan]")
                    for template in template_list:
                        console.print(f"  [yellow]{template['name']}[/yellow]: {template['description']}")
            else:
                console.print("[yellow]No templates found[/yellow]")
                
        except Exception as e:
            logger.exception("Error listing templates")
            console.print(f"[bold red]Error listing templates: {str(e)}[/bold red]")

@app.command()
def create_template(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the template"),
    description: str = typer.Option("", help="Description of the template"),
    from_resources: List[str] = typer.Option([], help="Resource IDs to include in the template"),
    output: str = typer.Option("templates", help="Directory to save the template")
) -> None:
    """
    Create a new template from existing resources
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("Creating template...", total=None)
        
        try:
            result = engine.create_template(
                name=name,
                description=description,
                resource_ids=from_resources,
                output_path=output
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                console.print(f"[bold green]Successfully created template '{name}':[/bold green]")
                console.print(f"Template saved to: {result.output}")
            else:
                console.print(f"[bold red]Failed to create template:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error creating template")
            console.print(f"[bold red]Error creating template: {str(e)}[/bold red]")

@app.command()
def check_compliance(
    ctx: typer.Context,
    service: str = typer.Argument(..., help="AWS service to check compliance for (e.g., iam, s3, ec2)"),
    resource_type: Optional[str] = typer.Option(None, help="Resource type to check (e.g., user, role, policy)"),
    resource_id: Optional[str] = typer.Option(None, help="Specific resource ID to check"),
    standard: str = typer.Option("pci-dss", help="Compliance standard to check against (pci-dss, hipaa, etc.)"),
    output_format: str = typer.Option("rich", help="Output format (rich, json, yaml, csv)"),
    report_file: Optional[str] = typer.Option(None, help="File to save the compliance report to"),
    severity_threshold: str = typer.Option("warning", help="Minimum severity level to report (info, warning, error)")
) -> None:
    """
    Check AWS resources for compliance with security standards
    """
    engine = initialize_app()
    
    with Progress(
        SpinnerColumn(), 
        TextColumn("[bold blue]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task(f"Checking {service} compliance against {standard}...", total=None)
        
        try:
            # Prepare parameters
            params = {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "standard": standard,
                "severity_threshold": severity_threshold
            }
            
            # Execute the check_compliance operation for the service
            result = engine.execute_operation(
                service=service,
                operation="check_compliance",
                **params
            )
            
            progress.update(task, completed=True)
            
            if result.success:
                # Display results
                if output_format == "rich":
                    _display_compliance_results(result.output, service, standard)
                elif output_format == "json":
                    import json
                    console.print(json.dumps(result.output, indent=2))
                elif output_format == "yaml":
                    import yaml
                    console.print(yaml.dump(result.output))
                elif output_format == "csv":
                    _export_compliance_csv(result.output, service, standard, report_file)
                
                # Save report if requested
                if report_file and output_format != "csv":
                    _save_compliance_report(result.output, report_file, output_format)
                    console.print(f"[green]Compliance report saved to {report_file}[/green]")
            else:
                console.print(f"[bold red]Failed to check {service} compliance:[/bold red]")
                console.print(f"[red]{result.error_message}[/red]")
                
        except Exception as e:
            logger.exception("Error checking compliance")
            console.print(f"[bold red]Error checking compliance: {str(e)}[/bold red]")

def _display_compliance_results(results: Dict[str, Any], service: str, standard: str) -> None:
    """
    Display compliance results in a rich format
    """
    from rich.table import Table
    
    console.print(f"[bold blue]Compliance Report: {service.upper()} against {standard.upper()}[/bold blue]")
    
    # Handle different result formats based on service
    if service == "iam":
        # Display password policy compliance
        if "password_policy" in results:
            pwd_policy = results["password_policy"]
            console.print("\n[bold]Password Policy:[/bold]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Status")
            table.add_column("Issue")
            
            if pwd_policy["compliant"]:
                table.add_row("[green]Compliant[/green]", "No issues found")
            else:
                for issue in pwd_policy["issues"]:
                    table.add_row("[red]Non-compliant[/red]", issue)
                    
            console.print(table)
        
        # Display MFA status
        if "mfa_status" in results:
            mfa_status = results["mfa_status"]
            console.print("\n[bold]MFA Status:[/bold]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Status")
            table.add_column("User")
            table.add_column("Admin")
            
            if mfa_status["compliant"]:
                table.add_row("[green]Compliant[/green]", "All users have MFA", "")
            else:
                for user in mfa_status["users_without_mfa"]:
                    is_admin = user in mfa_status["admin_users_without_mfa"]
                    admin_status = "[red]Yes[/red]" if is_admin else "No"
                    table.add_row("[red]Non-compliant[/red]", user, admin_status)
                    
            console.print(table)
            
        # Display policy compliance
        if "policies" in results:
            policy_status = results["policies"]
            console.print("\n[bold]Policy Status:[/bold]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Status")
            table.add_column("Policy Name")
            
            if policy_status["compliant"]:
                table.add_row("[green]Compliant[/green]", "No overly permissive policies found")
            else:
                for policy in policy_status["overly_permissive_policies"]:
                    table.add_row("[red]Non-compliant[/red]", policy)
                    
            console.print(table)
    else:
        # Generic handling for other services
        console.print(results)

def _export_compliance_csv(results: Dict[str, Any], service: str, standard: str, filename: Optional[str] = None) -> None:
    """
    Export compliance results to CSV format
    """
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Service", "Standard", "Resource Type", "Resource", "Status", "Issue"])
    
    # Handle different result formats based on service
    if service == "iam":
        # Process password policy results
        if "password_policy" in results:
            pwd_policy = results["password_policy"]
            if pwd_policy["compliant"]:
                writer.writerow(["iam", standard, "password_policy", "account", "Compliant", ""])
            else:
                for issue in pwd_policy["issues"]:
                    writer.writerow(["iam", standard, "password_policy", "account", "Non-compliant", issue])
        
        # Process MFA status results
        if "mfa_status" in results:
            mfa_status = results["mfa_status"]
            if mfa_status["compliant"]:
                writer.writerow(["iam", standard, "mfa", "all_users", "Compliant", ""])
            else:
                for user in mfa_status["users_without_mfa"]:
                    is_admin = user in mfa_status["admin_users_without_mfa"]
                    issue = "Missing MFA" + (" (Admin user)" if is_admin else "")
                    writer.writerow(["iam", standard, "mfa", user, "Non-compliant", issue])
        
        # Process policy results
        if "policies" in results:
            policy_status = results["policies"]
            if policy_status["compliant"]:
                writer.writerow(["iam", standard, "policy", "all_policies", "Compliant", ""])
            else:
                for policy in policy_status["overly_permissive_policies"]:
                    writer.writerow(["iam", standard, "policy", policy, "Non-compliant", "Overly permissive permissions"])
    else:
        # Generic handling for other services
        writer.writerow([service, standard, "unknown", "unknown", "Unknown", str(results)])
    
    # Write to file or print to console
    if filename:
        with open(filename, 'w', newline='') as f:
            f.write(output.getvalue())
    else:
        console.print(output.getvalue())

def _save_compliance_report(results: Dict[str, Any], filename: str, format: str) -> None:
    """
    Save compliance results to a file
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

if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unhandled exception")
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1) 