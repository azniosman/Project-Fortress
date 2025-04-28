#!/usr/bin/env python3

import boto3
import robo
from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ResourceStatus:
    name: str
    status: str
    details: Optional[str] = None

class ResourceVerifier:
    def __init__(self, environment: str):
        self.environment = environment
        self.cf_client = boto3.client('cloudformation')
        self.ec2_client = boto3.client('ec2')
        self.ecr_client = boto3.client('ecr')
        self.stack_name = f"project-fortress-base-{environment}"

    def verify_stack(self) -> ResourceStatus:
        """Verify CloudFormation stack status."""
        try:
            response = self.cf_client.describe_stacks(StackName=self.stack_name)
            stack = response['Stacks'][0]
            return ResourceStatus(
                name="CloudFormation Stack",
                status=stack['StackStatus'],
                details=f"Last updated: {stack.get('LastUpdatedTime', 'N/A')}"
            )
        except Exception as e:
            return ResourceStatus(
                name="CloudFormation Stack",
                status="ERROR",
                details=str(e)
            )

    def verify_vpc(self) -> ResourceStatus:
        """Verify VPC status."""
        try:
            response = self.ec2_client.describe_vpcs(
                Filters=[{'Name': 'tag:Name', 'Values': [f'project-fortress-{self.environment}-vpc']}]
            )
            if not response['Vpcs']:
                return ResourceStatus(
                    name="VPC",
                    status="NOT_FOUND"
                )
            
            vpc = response['Vpcs'][0]
            return ResourceStatus(
                name="VPC",
                status="ACTIVE" if vpc['State'] == 'available' else vpc['State'],
                details=f"CIDR: {vpc['CidrBlock']}"
            )
        except Exception as e:
            return ResourceStatus(
                name="VPC",
                status="ERROR",
                details=str(e)
            )

    def verify_subnets(self) -> List[ResourceStatus]:
        """Verify subnets status."""
        statuses = []
        try:
            response = self.ec2_client.describe_subnets(
                Filters=[{'Name': 'tag:Name', 'Values': [f'project-fortress-{self.environment}-*']}]
            )
            
            for subnet in response['Subnets']:
                name = next((tag['Value'] for tag in subnet['Tags'] 
                           if tag['Key'] == 'Name'), 'Unknown')
                statuses.append(ResourceStatus(
                    name=f"Subnet: {name}",
                    status="ACTIVE" if subnet['State'] == 'available' else subnet['State'],
                    details=f"CIDR: {subnet['CidrBlock']}"
                ))
        except Exception as e:
            statuses.append(ResourceStatus(
                name="Subnets",
                status="ERROR",
                details=str(e)
            ))
        
        return statuses

    def verify_ecr_repository(self) -> ResourceStatus:
        """Verify ECR repository status."""
        try:
            repo_name = f"project-fortress-{self.environment}"
            response = self.ecr_client.describe_repositories(
                repositoryNames=[repo_name]
            )
            repo = response['repositories'][0]
            return ResourceStatus(
                name="ECR Repository",
                status="ACTIVE",
                details=f"URI: {repo['repositoryUri']}"
            )
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            return ResourceStatus(
                name="ECR Repository",
                status="NOT_FOUND"
            )
        except Exception as e:
            return ResourceStatus(
                name="ECR Repository",
                status="ERROR",
                details=str(e)
            )

    def verify_all_resources(self) -> List[ResourceStatus]:
        """Verify all resources."""
        statuses = []
        
        # Verify stack
        statuses.append(self.verify_stack())
        
        # Verify VPC
        statuses.append(self.verify_vpc())
        
        # Verify subnets
        statuses.extend(self.verify_subnets())
        
        # Verify ECR repository
        statuses.append(self.verify_ecr_repository())
        
        return statuses

def main():
    robo.title("Project Fortress Resource Verification")
    
    # Environment selection
    environment = robo.select(
        "Select environment to verify:",
        options=["dev", "staging", "prod"],
        default="dev"
    )
    
    # Initialize verifier
    verifier = ResourceVerifier(environment)
    
    # Verify resources
    robo.info(f"\nVerifying resources for {environment} environment...")
    statuses = verifier.verify_all_resources()
    
    # Display results
    robo.info("\nVerification Results:")
    for status in statuses:
        if status.status == "ERROR":
            robo.error(f"{status.name}: {status.status}")
            if status.details:
                robo.error(f"  Details: {status.details}")
        elif status.status == "NOT_FOUND":
            robo.warning(f"{status.name}: {status.status}")
        else:
            robo.success(f"{status.name}: {status.status}")
            if status.details:
                robo.info(f"  Details: {status.details}")

if __name__ == "__main__":
    main() 