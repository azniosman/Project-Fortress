#!/usr/bin/env python3

import os
import sys
import json
import boto3
import robo
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class StackConfig:
    name: str
    template_file: str
    region: str
    parameters: Dict[str, str]

class DeploymentManager:
    def __init__(self):
        self.cf_client = boto3.client('cloudformation')
        self.ec2_client = boto3.client('ec2')
        self.ecr_client = boto3.client('ecr')
        
    def validate_template(self, template_path: str) -> bool:
        """Validate CloudFormation template."""
        try:
            with open(template_path, 'r') as f:
                template_body = f.read()
            self.cf_client.validate_template(TemplateBody=template_body)
            return True
        except Exception as e:
            robo.error(f"Template validation failed: {str(e)}")
            return False

    def check_stack_exists(self, stack_name: str) -> bool:
        """Check if stack exists."""
        try:
            self.cf_client.describe_stacks(StackName=stack_name)
            return True
        except self.cf_client.exceptions.ClientError as e:
            if "does not exist" in str(e):
                return False
            raise

    def create_stack(self, config: StackConfig) -> bool:
        """Create or update CloudFormation stack."""
        try:
            with open(config.template_file, 'r') as f:
                template_body = f.read()

            stack_name = f"{config.name}-{config.parameters['Environment']}"
            
            if self.check_stack_exists(stack_name):
                robo.info(f"Stack {stack_name} exists. Updating...")
                self.cf_client.update_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[{'ParameterKey': k, 'ParameterValue': v} 
                              for k, v in config.parameters.items()],
                    Capabilities=['CAPABILITY_IAM']
                )
            else:
                robo.info(f"Creating new stack: {stack_name}")
                self.cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[{'ParameterKey': k, 'ParameterValue': v} 
                              for k, v in config.parameters.items()],
                    Capabilities=['CAPABILITY_IAM']
                )

            robo.info("Waiting for stack operation to complete...")
            waiter = self.cf_client.get_waiter('stack_create_complete' 
                                             if not self.check_stack_exists(stack_name) 
                                             else 'stack_update_complete')
            waiter.wait(StackName=stack_name)
            
            return True
        except Exception as e:
            robo.error(f"Stack operation failed: {str(e)}")
            return False

    def get_stack_outputs(self, stack_name: str) -> Optional[List[Dict]]:
        """Get stack outputs."""
        try:
            response = self.cf_client.describe_stacks(StackName=stack_name)
            return response['Stacks'][0]['Outputs']
        except Exception as e:
            robo.error(f"Failed to get stack outputs: {str(e)}")
            return None

def get_environment_config(environment: str) -> StackConfig:
    """Get configuration for specified environment."""
    base_path = Path(__file__).parent.parent
    template_file = str(base_path / "cloudformation" / "base-stack.yml")
    
    return StackConfig(
        name="project-fortress-base",
        template_file=template_file,
        region="us-east-1",
        parameters={
            "Environment": environment,
            "VPCCidrBlock": "10.0.0.0/16",
            "PublicSubnet1CidrBlock": "10.0.1.0/24",
            "PrivateSubnet1CidrBlock": "10.0.2.0/24"
        }
    )

def main():
    robo.title("Project Fortress Deployment")
    
    # Environment selection
    environment = robo.select(
        "Select environment:",
        options=["dev", "staging", "prod"],
        default="dev"
    )
    
    # Initialize deployment manager
    manager = DeploymentManager()
    
    # Get configuration
    config = get_environment_config(environment)
    
    # Validate template
    if not manager.validate_template(config.template_file):
        robo.error("Template validation failed. Exiting...")
        sys.exit(1)
    
    # Confirm deployment
    if not robo.confirm(f"Deploy to {environment} environment?"):
        robo.info("Deployment cancelled")
        sys.exit(0)
    
    # Deploy stack
    if manager.create_stack(config):
        stack_name = f"{config.name}-{environment}"
        outputs = manager.get_stack_outputs(stack_name)
        
        if outputs:
            robo.info("\nStack Outputs:")
            for output in outputs:
                robo.info(f"{output['OutputKey']}: {output['OutputValue']}")
        
        robo.success("Deployment completed successfully!")
    else:
        robo.error("Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 