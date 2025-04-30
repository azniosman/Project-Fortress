#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EC2 Service Module - Manages EC2 instances

This module provides functionality to create, list, update, and delete EC2 instances.
"""

import boto3
import logging
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional

from core.plugin_manager import ServiceModule
from utils.logger import setup_logger
from utils.validators import validate_ec2_instance_type, validate_tags

class EC2ServiceModule(ServiceModule):
    """
    EC2 Service Module for managing EC2 instances
    """
    
    def __init__(self):
        """
        Initialize the EC2 service module
        """
        super().__init__("ec2", "EC2 Instances")
        self.logger = setup_logger(f"service.{self.service_name}")
    
    def get_operations(self) -> List[str]:
        """
        Get the list of operations supported by this service module
        
        Returns:
            List of operation names
        """
        return ["create", "list", "update", "delete", "describe", "export", "check_permissions"]
    
    def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an operation on this service
        
        Args:
            operation: The operation to execute
            **kwargs: Operation-specific parameters
            
        Returns:
            Dictionary with operation result
        """
        if operation == "create":
            return self.create_instance(**kwargs)
        elif operation == "list":
            return self.list_instances(**kwargs)
        elif operation == "update":
            return self.update_instance(**kwargs)
        elif operation == "delete":
            return self.delete_instance(**kwargs)
        elif operation == "describe":
            return self.describe_instance(**kwargs)
        elif operation == "export":
            return self.export_instances(**kwargs)
        elif operation == "check_permissions":
            return self.check_permissions(**kwargs)
        else:
            return {
                "success": False,
                "error": f"Operation '{operation}' not supported by EC2 service module"
            }
    
    def create_instance(
        self,
        resource_name: Optional[str] = None,
        template_config: Optional[Dict[str, Any]] = None,
        guided: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Create an EC2 instance
        
        Args:
            resource_name: Optional name for the instance
            template_config: Optional template configuration
            guided: Whether to use guided wizard mode
            dry_run: Whether to validate without creating
            
        Returns:
            Dictionary with operation result
        """
        try:
            region = boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=region)
            
            # Determine parameters (from template or defaults)
            params = {}
            if template_config:
                params = template_config.get("parameters", {})
            
            # Set instance name if provided
            if resource_name:
                params["TagSpecifications"] = [{
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": resource_name}]
                }]
            
            # Set instance type (default to t2.micro if not specified)
            instance_type = params.get("InstanceType", "t2.micro")
            
            # Validate instance type
            if not validate_ec2_instance_type(instance_type):
                return {
                    "success": False,
                    "error": f"Invalid instance type: {instance_type}"
                }
            
            # Set ImageId (default to Amazon Linux 2)
            image_id = params.get("ImageId")
            if not image_id:
                # Get latest Amazon Linux 2 AMI
                response = ec2.describe_images(
                    Owners=["amazon"],
                    Filters=[
                        {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
                        {"Name": "state", "Values": ["available"]}
                    ]
                )
                
                # Sort by creation date and get the latest
                images = sorted(
                    response["Images"],
                    key=lambda x: x["CreationDate"],
                    reverse=True
                )
                
                if images:
                    image_id = images[0]["ImageId"]
                else:
                    return {
                        "success": False,
                        "error": "Could not find suitable Amazon Linux 2 AMI"
                    }
                
                params["ImageId"] = image_id
            
            # Set up parameters for RunInstances
            run_params = {
                "ImageId": params.get("ImageId"),
                "InstanceType": instance_type,
                "MinCount": 1,
                "MaxCount": 1,
                "DryRun": dry_run
            }
            
            # Add KeyName if specified
            if "KeyName" in params:
                run_params["KeyName"] = params["KeyName"]
            
            # Add SecurityGroupIds if specified
            if "SecurityGroupIds" in params:
                run_params["SecurityGroupIds"] = params["SecurityGroupIds"]
            
            # Add SubnetId if specified
            if "SubnetId" in params:
                run_params["SubnetId"] = params["SubnetId"]
            
            # Add TagSpecifications if specified
            if "TagSpecifications" in params:
                run_params["TagSpecifications"] = params["TagSpecifications"]
            
            # Add UserData if specified
            if "UserData" in params:
                run_params["UserData"] = params["UserData"]
            
            # Launch instance
            response = ec2.run_instances(**run_params)
            
            # Extract instance ID
            instance_id = response["Instances"][0]["InstanceId"]
            
            return {
                "success": True,
                "output": {
                    "instance_id": instance_id,
                    "region": region
                }
            }
            
        except ClientError as e:
            if e.response["Error"]["Code"] == "DryRunOperation":
                return {
                    "success": True,
                    "output": "Dry run successful"
                }
            else:
                self.logger.error(f"Error creating EC2 instance: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error creating EC2 instance: {str(e)}"
                }
        except Exception as e:
            self.logger.error(f"Error creating EC2 instance: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating EC2 instance: {str(e)}"
            }
    
    def list_instances(
        self,
        output_format: str = "rich",
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List EC2 instances
        
        Args:
            output_format: Output format (rich, json, yaml)
            filter_expr: Optional filter expression
            
        Returns:
            Dictionary with operation result
        """
        try:
            region = boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=region)
            
            # Parse filter expression
            filters = []
            if filter_expr:
                # Format: Name=value,Name=value
                for f in filter_expr.split(","):
                    if "=" in f:
                        key, value = f.split("=", 1)
                        filters.append({"Name": key, "Values": [value]})
            
            # Describe instances
            response = ec2.describe_instances(Filters=filters)
            
            # Extract instance information
            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_info = {
                        "InstanceId": instance["InstanceId"],
                        "InstanceType": instance["InstanceType"],
                        "State": instance["State"]["Name"],
                        "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
                        "PublicIpAddress": instance.get("PublicIpAddress", "N/A"),
                        "PrivateIpAddress": instance.get("PrivateIpAddress", "N/A")
                    }
                    
                    # Add name tag if present
                    name = "N/A"
                    for tag in instance.get("Tags", []):
                        if tag["Key"] == "Name":
                            name = tag["Value"]
                            break
                    
                    instance_info["Name"] = name
                    instances.append(instance_info)
            
            return {
                "success": True,
                "output": instances
            }
            
        except Exception as e:
            self.logger.error(f"Error listing EC2 instances: {str(e)}")
            return {
                "success": False,
                "error": f"Error listing EC2 instances: {str(e)}"
            }
    
    def update_instance(
        self,
        resource_id: str,
        parameters: Dict[str, Any],
        guided: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Update an EC2 instance
        
        Args:
            resource_id: The ID of the instance to update
            parameters: Parameters to update
            guided: Whether to use guided wizard mode
            dry_run: Whether to validate without updating
            
        Returns:
            Dictionary with operation result
        """
        try:
            region = boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=region)
            
            # Process parameters
            updated_params = {}
            
            # Handle instance type update
            if "instance_type" in parameters:
                instance_type = parameters["instance_type"]
                
                # Validate instance type
                if not validate_ec2_instance_type(instance_type):
                    return {
                        "success": False,
                        "error": f"Invalid instance type: {instance_type}"
                    }
                
                # Update instance type
                ec2.modify_instance_attribute(
                    InstanceId=resource_id,
                    InstanceType={"Value": instance_type},
                    DryRun=dry_run
                )
                
                updated_params["instance_type"] = instance_type
            
            # Handle security group update
            if "security_groups" in parameters:
                security_groups = parameters["security_groups"]
                
                # Update security groups
                ec2.modify_instance_attribute(
                    InstanceId=resource_id,
                    Groups=security_groups,
                    DryRun=dry_run
                )
                
                updated_params["security_groups"] = security_groups
            
            # Handle tags update
            if "tags" in parameters:
                tags = parameters["tags"]
                
                # Validate tags
                is_valid, error = validate_tags(tags)
                if not is_valid:
                    return {
                        "success": False,
                        "error": f"Invalid tags: {error}"
                    }
                
                # Format tags for EC2 API
                tag_specifications = []
                for key, value in tags.items():
                    tag_specifications.append({"Key": key, "Value": value})
                
                # Update tags
                ec2.create_tags(
                    Resources=[resource_id],
                    Tags=tag_specifications,
                    DryRun=dry_run
                )
                
                updated_params["tags"] = tags
            
            return {
                "success": True,
                "output": {
                    "instance_id": resource_id,
                    "updated_params": updated_params
                }
            }
            
        except ClientError as e:
            if e.response["Error"]["Code"] == "DryRunOperation":
                return {
                    "success": True,
                    "output": "Dry run successful"
                }
            else:
                self.logger.error(f"Error updating EC2 instance: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error updating EC2 instance: {str(e)}"
                }
        except Exception as e:
            self.logger.error(f"Error updating EC2 instance: {str(e)}")
            return {
                "success": False,
                "error": f"Error updating EC2 instance: {str(e)}"
            }
    
    def delete_instance(
        self,
        resource_id: str,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Delete an EC2 instance
        
        Args:
            resource_id: The ID of the instance to delete
            dry_run: Whether to validate without deleting
            
        Returns:
            Dictionary with operation result
        """
        try:
            region = boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=region)
            
            # Terminate instance
            ec2.terminate_instances(
                InstanceIds=[resource_id],
                DryRun=dry_run
            )
            
            return {
                "success": True,
                "output": {
                    "instance_id": resource_id,
                    "status": "terminating"
                }
            }
            
        except ClientError as e:
            if e.response["Error"]["Code"] == "DryRunOperation":
                return {
                    "success": True,
                    "output": "Dry run successful"
                }
            else:
                self.logger.error(f"Error deleting EC2 instance: {str(e)}")
                return {
                    "success": False,
                    "error": f"Error deleting EC2 instance: {str(e)}"
                }
        except Exception as e:
            self.logger.error(f"Error deleting EC2 instance: {str(e)}")
            return {
                "success": False,
                "error": f"Error deleting EC2 instance: {str(e)}"
            }
    
    def describe_instance(
        self,
        resource_id: str
    ) -> Dict[str, Any]:
        """
        Describe an EC2 instance
        
        Args:
            resource_id: The ID of the instance to describe
            
        Returns:
            Dictionary with operation result
        """
        try:
            region = boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=region)
            
            # Describe instance
            response = ec2.describe_instances(InstanceIds=[resource_id])
            
            # Extract instance information
            if not response["Reservations"] or not response["Reservations"][0]["Instances"]:
                return {
                    "success": False,
                    "error": f"Instance {resource_id} not found"
                }
            
            instance = response["Reservations"][0]["Instances"][0]
            
            instance_info = {
                "InstanceId": instance["InstanceId"],
                "InstanceType": instance["InstanceType"],
                "ImageId": instance["ImageId"],
                "State": instance["State"]["Name"],
                "AvailabilityZone": instance["Placement"]["AvailabilityZone"],
                "PublicIpAddress": instance.get("PublicIpAddress", "N/A"),
                "PrivateIpAddress": instance.get("PrivateIpAddress", "N/A"),
                "SecurityGroups": instance.get("SecurityGroups", []),
                "Tags": instance.get("Tags", [])
            }
            
            return {
                "success": True,
                "output": instance_info
            }
            
        except Exception as e:
            self.logger.error(f"Error describing EC2 instance: {str(e)}")
            return {
                "success": False,
                "error": f"Error describing EC2 instance: {str(e)}"
            }
    
    def export_instances(
        self,
        export_format: str,
        output_path: str,
        resource_ids: Optional[List[str]] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export EC2 instances as Infrastructure as Code
        
        Args:
            export_format: Export format (terraform, cloudformation, cdk)
            output_path: Output directory or file
            resource_ids: Optional list of instance IDs to export
            region: Optional AWS region of instances
            
        Returns:
            Dictionary with operation result
        """
        try:
            if export_format not in ["terraform", "cloudformation", "cdk"]:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {export_format}"
                }
            
            # Use specified region or default
            use_region = region or boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=use_region)
            
            # Get instances to export
            filters = []
            instances_response = ec2.describe_instances(
                InstanceIds=resource_ids if resource_ids else [],
                Filters=filters
            )
            
            # Extract instance information
            instances = []
            for reservation in instances_response["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append(instance)
            
            # Generate output based on format
            output_content = ""
            
            if export_format == "terraform":
                output_content = self._generate_terraform(instances, use_region)
            elif export_format == "cloudformation":
                output_content = self._generate_cloudformation(instances, use_region)
            elif export_format == "cdk":
                output_content = self._generate_cdk(instances, use_region)
            
            # Determine output file
            import os
            if os.path.isdir(output_path):
                if export_format == "terraform":
                    output_file = os.path.join(output_path, "ec2.tf")
                elif export_format == "cloudformation":
                    output_file = os.path.join(output_path, "ec2.yaml")
                elif export_format == "cdk":
                    output_file = os.path.join(output_path, "ec2.py")
            else:
                output_file = output_path
            
            # Write output
            with open(output_file, "w") as f:
                f.write(output_content)
            
            return {
                "success": True,
                "output": output_file
            }
            
        except Exception as e:
            self.logger.error(f"Error exporting EC2 instances: {str(e)}")
            return {
                "success": False,
                "error": f"Error exporting EC2 instances: {str(e)}"
            }
    
    def _generate_terraform(self, instances: List[Dict[str, Any]], region: str) -> str:
        """
        Generate Terraform code for EC2 instances
        
        Args:
            instances: List of EC2 instance data
            region: AWS region
            
        Returns:
            Terraform code as a string
        """
        terraform_code = f"""# EC2 Instances - Generated by AWS Resource Manager
provider "aws" {{
  region = "{region}"
}}

"""
        
        for instance in instances:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            ami = instance["ImageId"]
            
            # Get name from tags if available
            name = instance_id
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            
            # Clean name for Terraform resource ID
            resource_id = "".join(c if c.isalnum() else "_" for c in name)
            
            # Generate security group IDs
            sg_ids = [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
            sg_ids_str = ", ".join([f'"{sg_id}"' for sg_id in sg_ids])
            
            # Generate subnet ID
            subnet_id = instance.get("SubnetId", "")
            
            # Generate tags
            tags_str = ""
            for tag in instance.get("Tags", []):
                tags_str += f'    {tag["Key"]} = "{tag["Value"]}"\n'
            
            terraform_code += f"""resource "aws_instance" "{resource_id}" {{
  ami           = "{ami}"
  instance_type = "{instance_type}"
  {"subnet_id     = \"" + subnet_id + "\"" if subnet_id else ""}
  {"vpc_security_group_ids = [" + sg_ids_str + "]" if sg_ids else ""}
  
  tags = {{
{tags_str}  }}
}}

"""
        
        return terraform_code
    
    def _generate_cloudformation(self, instances: List[Dict[str, Any]], region: str) -> str:
        """
        Generate CloudFormation template for EC2 instances
        
        Args:
            instances: List of EC2 instance data
            region: AWS region
            
        Returns:
            CloudFormation template as a string
        """
        import yaml
        
        cf_template = {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": "EC2 Instances - Generated by AWS Resource Manager",
            "Resources": {}
        }
        
        for instance in instances:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            ami = instance["ImageId"]
            
            # Get name from tags if available
            name = instance_id
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            
            # Clean name for CloudFormation resource ID
            resource_id = "".join(c if c.isalnum() else "" for c in name)
            
            # Generate security group IDs
            sg_ids = [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
            
            # Generate subnet ID
            subnet_id = instance.get("SubnetId", "")
            
            # Generate tags
            tags = []
            for tag in instance.get("Tags", []):
                tags.append({"Key": tag["Key"], "Value": tag["Value"]})
            
            # Create resource definition
            resource_def = {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "ImageId": ami,
                    "InstanceType": instance_type,
                    "Tags": tags
                }
            }
            
            if subnet_id:
                resource_def["Properties"]["SubnetId"] = subnet_id
            
            if sg_ids:
                resource_def["Properties"]["SecurityGroupIds"] = sg_ids
            
            cf_template["Resources"][resource_id] = resource_def
        
        return yaml.dump(cf_template, default_flow_style=False)
    
    def _generate_cdk(self, instances: List[Dict[str, Any]], region: str) -> str:
        """
        Generate CDK code for EC2 instances
        
        Args:
            instances: List of EC2 instance data
            region: AWS region
            
        Returns:
            CDK code as a string
        """
        cdk_code = f"""# EC2 Instances - Generated by AWS Resource Manager
from aws_cdk import (
    core,
    aws_ec2 as ec2,
)

class EC2InstancesStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
"""
        
        for instance in instances:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            ami = instance["ImageId"]
            
            # Get name from tags if available
            name = instance_id
            for tag in instance.get("Tags", []):
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break
            
            # Clean name for CDK variable name
            var_name = "".join(c if c.isalnum() else "_" for c in name.lower())
            
            # Generate security group IDs
            sg_ids = [sg["GroupId"] for sg in instance.get("SecurityGroups", [])]
            
            # Generate subnet ID
            subnet_id = instance.get("SubnetId", "")
            
            # Generate tags
            tags_str = ""
            for tag in instance.get("Tags", []):
                tags_str += f'            "{tag["Key"]}": "{tag["Value"]}",\n'
            
            cdk_code += f"""        # {name} instance
        {var_name} = ec2.Instance(self, "{name}",
            instance_type=ec2.InstanceType("{instance_type}"),
            machine_image=ec2.MachineImage.generic_linux({{
                "{region}": "{ami}"
            }}),
"""
            
            if subnet_id:
                cdk_code += f"""            vpc_subnets=ec2.SubnetSelection(subnet_id="{subnet_id}"),
"""
            
            if sg_ids:
                sg_ids_str = ", ".join([f'security_group_{i}' for i in range(len(sg_ids))])
                
                for i, sg_id in enumerate(sg_ids):
                    cdk_code += f"""            security_group_{i}=ec2.SecurityGroup.from_security_group_id(self, "{var_name}_sg_{i}", "{sg_id}"),
"""
            
            cdk_code += f"""        )
        
        # Add tags
        core.Tags.of({var_name}).add_all({{
{tags_str}        }})
        
"""
        
        cdk_code += """
app = core.App()
EC2InstancesStack(app, "EC2InstancesStack")
app.synth()
"""
        
        return cdk_code
    
    def check_permissions(self) -> Dict[str, Any]:
        """
        Check AWS permissions for EC2 operations
        
        Returns:
            Dictionary with operation result
        """
        try:
            region = boto3.session.Session().region_name
            ec2 = boto3.client("ec2", region_name=region)
            
            # Required permissions to check
            permissions_to_check = [
                "ec2:DescribeInstances",
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:ModifyInstanceAttribute",
                "ec2:CreateTags"
            ]
            
            # Check each permission
            missing_permissions = []
            
            # Check DescribeInstances
            try:
                ec2.describe_instances(MaxResults=5)
            except ClientError as e:
                if e.response["Error"]["Code"] == "UnauthorizedOperation":
                    missing_permissions.append("ec2:DescribeInstances")
            
            # Check RunInstances with DryRun
            try:
                ec2.run_instances(
                    ImageId="ami-12345678",
                    InstanceType="t2.micro",
                    MinCount=1,
                    MaxCount=1,
                    DryRun=True
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "UnauthorizedOperation":
                    missing_permissions.append("ec2:RunInstances")
            
            # Check TerminateInstances with DryRun
            try:
                ec2.terminate_instances(
                    InstanceIds=["i-12345678"],
                    DryRun=True
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "UnauthorizedOperation":
                    missing_permissions.append("ec2:TerminateInstances")
            
            # Check ModifyInstanceAttribute with DryRun
            try:
                ec2.modify_instance_attribute(
                    InstanceId="i-12345678",
                    InstanceType={"Value": "t2.micro"},
                    DryRun=True
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "UnauthorizedOperation":
                    missing_permissions.append("ec2:ModifyInstanceAttribute")
            
            # Check CreateTags with DryRun
            try:
                ec2.create_tags(
                    Resources=["i-12345678"],
                    Tags=[{"Key": "test", "Value": "test"}],
                    DryRun=True
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "UnauthorizedOperation":
                    missing_permissions.append("ec2:CreateTags")
            
            if missing_permissions:
                return {
                    "success": False,
                    "error": f"Missing permissions: {', '.join(missing_permissions)}"
                }
            
            return {
                "success": True,
                "output": "All required permissions are granted"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking EC2 permissions: {str(e)}")
            return {
                "success": False,
                "error": f"Error checking EC2 permissions: {str(e)}"
            } 