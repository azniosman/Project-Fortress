#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IAM Service Module - Manages AWS IAM resources

This module provides functionality to create, list, update, and delete IAM users, roles, and policies,
with a focus on security best practices for FinTech applications.
"""

import boto3
import json
import logging
from botocore.exceptions import ClientError
from typing import Dict, List, Any, Optional, Tuple

from core.plugin_manager import ServiceModule
from utils.logger import setup_logger
from utils.validators import validate_iam_policy, validate_tags

class IAMServiceModule(ServiceModule):
    """
    IAM Service Module for managing AWS IAM resources
    """
    
    def __init__(self):
        """
        Initialize the IAM service module
        """
        super().__init__("iam", "IAM Resources")
        self.logger = setup_logger(f"service.{self.service_name}")
        self.pci_dss_requirements = {
            "password_policy": {
                "min_length": 8,
                "require_symbols": True,
                "require_numbers": True,
                "require_uppercase": True,
                "require_lowercase": True,
                "max_age": 90,
                "prevent_reuse": 24
            }
        }
    
    def get_operations(self) -> List[str]:
        """
        Get the list of operations supported by this service module
        
        Returns:
            List of operation names
        """
        return [
            "create", "list", "update", "delete", "describe", "export",
            "check_permissions", "check_compliance", "create_policy",
            "attach_policy", "enable_mfa", "rotate_credentials"
        ]
    
    def execute_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an operation on this service
        
        Args:
            operation: The operation to execute
            **kwargs: Operation-specific parameters
            
        Returns:
            Dictionary with operation result
        """
        operations_map = {
            "create": self.create_resource,
            "list": self.list_resources,
            "update": self.update_resource,
            "delete": self.delete_resource,
            "describe": self.describe_resource,
            "export": self.export_resources,
            "check_permissions": self.check_permissions,
            "check_compliance": self.check_compliance,
            "create_policy": self.create_policy,
            "attach_policy": self.attach_policy,
            "enable_mfa": self.enable_mfa,
            "rotate_credentials": self.rotate_credentials
        }
        
        if operation in operations_map:
            return operations_map[operation](**kwargs)
        else:
            return {
                "success": False,
                "error": f"Operation '{operation}' not supported by IAM service module"
            }
    
    def create_resource(
        self,
        resource_type: str,
        resource_name: str,
        template_config: Optional[Dict[str, Any]] = None,
        guided: bool = False,
        dry_run: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create an IAM resource (user, role, or policy)
        
        Args:
            resource_type: Type of resource (user, role, policy)
            resource_name: Name for the resource
            template_config: Optional template configuration
            guided: Whether to use guided wizard mode
            dry_run: Whether to validate without creating
            
        Returns:
            Dictionary with operation result
        """
        try:
            session = boto3.session.Session()
            region = session.region_name
            iam = session.client("iam")
            
            # Determine parameters (from template or defaults)
            params = {}
            if template_config:
                params = template_config.get("parameters", {})
            
            # Process specific resource type
            if resource_type == "user":
                return self._create_user(iam, resource_name, params, dry_run)
            elif resource_type == "role":
                return self._create_role(iam, resource_name, params, dry_run)
            elif resource_type == "policy":
                return self._create_policy(iam, resource_name, params, dry_run)
            else:
                return {
                    "success": False,
                    "error": f"Invalid resource type: {resource_type}. Must be one of: user, role, policy"
                }
                
        except ClientError as e:
            self.logger.error(f"Error creating IAM {resource_type}: {str(e)}")
            return {
                "success": False,
                "error": f"Error creating IAM {resource_type}: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error creating IAM {resource_type}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error creating IAM {resource_type}: {str(e)}"
            }
    
    def _create_user(self, iam, user_name: str, params: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Create an IAM user with secure defaults for FinTech applications"""
        if dry_run:
            return {"success": True, "output": "Dry run successful for IAM user creation"}
            
        # Create user
        iam.create_user(UserName=user_name)
        
        # Add user to specified groups
        if "Groups" in params and params["Groups"]:
            for group_name in params["Groups"]:
                try:
                    iam.add_user_to_group(
                        GroupName=group_name,
                        UserName=user_name
                    )
                except ClientError as e:
                    self.logger.warning(f"Could not add user to group {group_name}: {str(e)}")
        
        # Apply tags if specified
        if "Tags" in params and params["Tags"]:
            iam.tag_user(
                UserName=user_name,
                Tags=[{"Key": k, "Value": v} for k, v in params["Tags"].items()]
            )
        
        # Create access key if specified (PCI compliance requires careful handling)
        create_access_key = params.get("CreateAccessKey", False)
        access_key_data = None
        
        if create_access_key:
            response = iam.create_access_key(UserName=user_name)
            access_key_data = {
                "AccessKeyId": response["AccessKey"]["AccessKeyId"],
                "SecretAccessKey": response["AccessKey"]["SecretAccessKey"]
            }
            self.logger.warning("Access key created. Please store securely and enable key rotation.")
        
        # Enable console access if specified
        if params.get("ConsoleAccess", False):
            # Generate a secure random password
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
            password = ''.join(secrets.choice(alphabet) for _ in range(16))
            
            # Create login profile
            iam.create_login_profile(
                UserName=user_name,
                Password=password,
                PasswordResetRequired=True
            )
            
            return {
                "success": True,
                "output": {
                    "user_name": user_name,
                    "console_password": password,
                    "access_key": access_key_data,
                    "notes": "Password reset required on first login. Store credentials securely!"
                }
            }
            
        return {
            "success": True,
            "output": {
                "user_name": user_name,
                "access_key": access_key_data
            }
        }
    
    def _create_role(self, iam, role_name: str, params: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Create an IAM role with trust policy"""
        if dry_run:
            return {"success": True, "output": "Dry run successful for IAM role creation"}
            
        # Validate and get trust policy
        trust_policy = params.get("TrustPolicy")
        if not trust_policy:
            # Default to EC2 trust policy if not specified
            trust_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
            
        # Create role
        response = iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=params.get("Description", f"Role for {role_name}")
        )
        
        # Apply tags if specified
        if "Tags" in params and params["Tags"]:
            iam.tag_role(
                RoleName=role_name,
                Tags=[{"Key": k, "Value": v} for k, v in params["Tags"].items()]
            )
            
        # Attach managed policies if specified
        if "ManagedPolicies" in params and params["ManagedPolicies"]:
            for policy_arn in params["ManagedPolicies"]:
                iam.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                
        return {
            "success": True,
            "output": {
                "role_name": role_name,
                "role_arn": response["Role"]["Arn"]
            }
        }
    
    def _create_policy(self, iam, policy_name: str, params: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Create an IAM policy with the specified policy document"""
        if dry_run:
            return {"success": True, "output": "Dry run successful for IAM policy creation"}
            
        # Get and validate policy document
        policy_doc = params.get("PolicyDocument")
        if not policy_doc:
            return {
                "success": False,
                "error": "Policy document is required for policy creation"
            }
            
        # Validate policy document
        if not validate_iam_policy(policy_doc):
            return {
                "success": False,
                "error": "Invalid policy document format or content"
            }
            
        # Create policy
        response = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_doc),
            Description=params.get("Description", f"Policy for {policy_name}")
        )
        
        # Apply tags if specified
        if "Tags" in params and params["Tags"]:
            iam.tag_policy(
                PolicyArn=response["Policy"]["Arn"],
                Tags=[{"Key": k, "Value": v} for k, v in params["Tags"].items()]
            )
            
        return {
            "success": True,
            "output": {
                "policy_name": policy_name,
                "policy_arn": response["Policy"]["Arn"],
                "policy_id": response["Policy"]["PolicyId"]
            }
        }
    
    def list_resources(
        self,
        resource_type: str,
        output_format: str = "rich",
        filter_expr: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List IAM resources of the specified type
        
        Args:
            resource_type: Type of resource (user, role, policy, group)
            output_format: Output format (rich, json, yaml)
            filter_expr: Optional filter expression
            
        Returns:
            Dictionary with operation result
        """
        try:
            session = boto3.session.Session()
            iam = session.client("iam")
            
            # Process specific resource type
            if resource_type == "user":
                response = iam.list_users()
                resources = response.get("Users", [])
            elif resource_type == "role":
                response = iam.list_roles()
                resources = response.get("Roles", [])
            elif resource_type == "policy":
                response = iam.list_policies(Scope="Local")
                resources = response.get("Policies", [])
            elif resource_type == "group":
                response = iam.list_groups()
                resources = response.get("Groups", [])
            else:
                return {
                    "success": False,
                    "error": f"Invalid resource type: {resource_type}. Must be one of: user, role, policy, group"
                }
                
            # Apply filter if specified
            if filter_expr:
                import re
                parts = filter_expr.split("=")
                if len(parts) == 2:
                    key, value = parts
                    resources = [r for r in resources if key in r and re.search(value, str(r[key]))]
            
            return {
                "success": True,
                "output": resources
            }
                
        except ClientError as e:
            self.logger.error(f"Error listing IAM {resource_type}s: {str(e)}")
            return {
                "success": False,
                "error": f"Error listing IAM {resource_type}s: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error listing IAM {resource_type}s: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error listing IAM {resource_type}s: {str(e)}"
            }
    
    def check_compliance(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check PCI-DSS and security best practices compliance for IAM resources
        
        Args:
            resource_type: Optional type of resource to check
            resource_id: Optional specific resource ID to check
            
        Returns:
            Dictionary with compliance check results
        """
        try:
            session = boto3.session.Session()
            iam = session.client("iam")
            
            compliance_results = {}
            
            # Check account password policy
            try:
                response = iam.get_account_password_policy()
                policy = response["PasswordPolicy"]
                
                # Check against PCI-DSS requirements
                pci_req = self.pci_dss_requirements["password_policy"]
                password_issues = []
                
                if policy.get("MinimumPasswordLength", 0) < pci_req["min_length"]:
                    password_issues.append(f"Password minimum length ({policy.get('MinimumPasswordLength', 0)}) is less than PCI-DSS recommended ({pci_req['min_length']})")
                
                if not policy.get("RequireSymbols", False) and pci_req["require_symbols"]:
                    password_issues.append("Symbols are not required in passwords")
                    
                if not policy.get("RequireNumbers", False) and pci_req["require_numbers"]:
                    password_issues.append("Numbers are not required in passwords")
                    
                if not policy.get("RequireUppercaseCharacters", False) and pci_req["require_uppercase"]:
                    password_issues.append("Uppercase characters are not required in passwords")
                    
                if not policy.get("RequireLowercaseCharacters", False) and pci_req["require_lowercase"]:
                    password_issues.append("Lowercase characters are not required in passwords")
                
                if policy.get("MaxPasswordAge", 999) > pci_req["max_age"]:
                    password_issues.append(f"Password expiration time ({policy.get('MaxPasswordAge', 'not set')}) exceeds PCI-DSS recommendation ({pci_req['max_age']} days)")
                
                if policy.get("PasswordReusePrevention", 0) < pci_req["prevent_reuse"]:
                    password_issues.append(f"Password reuse prevention ({policy.get('PasswordReusePrevention', 'not set')}) is less than PCI-DSS recommended ({pci_req['prevent_reuse']})")
                
                compliance_results["password_policy"] = {
                    "compliant": len(password_issues) == 0,
                    "issues": password_issues
                }
                
            except ClientError as e:
                if "NoSuchEntity" in str(e):
                    compliance_results["password_policy"] = {
                        "compliant": False,
                        "issues": ["No account password policy is set. This violates PCI-DSS requirements."]
                    }
                else:
                    raise e
                    
            # Check MFA for users
            if not resource_type or resource_type == "user":
                users = iam.list_users()["Users"]
                
                users_without_mfa = []
                admin_users_without_mfa = []
                
                for user in users:
                    user_name = user["UserName"]
                    
                    # Skip checking specific user if not the requested one
                    if resource_id and user_name != resource_id:
                        continue
                        
                    # Check if MFA is enabled
                    mfa_devices = iam.list_mfa_devices(UserName=user_name)["MFADevices"]
                    if not mfa_devices:
                        users_without_mfa.append(user_name)
                        
                        # Check if user has admin privileges
                        attached_policies = iam.list_attached_user_policies(UserName=user_name)["AttachedPolicies"]
                        admin_policy = any(p["PolicyArn"] == "arn:aws:iam::aws:policy/AdministratorAccess" for p in attached_policies)
                        
                        if admin_policy:
                            admin_users_without_mfa.append(user_name)
                
                compliance_results["mfa_status"] = {
                    "compliant": len(users_without_mfa) == 0,
                    "users_without_mfa": users_without_mfa,
                    "admin_users_without_mfa": admin_users_without_mfa
                }
                
            # Check for any policies allowing full admin access
            if not resource_type or resource_type == "policy":
                policies = iam.list_policies(Scope="Local")["Policies"]
                
                overly_permissive_policies = []
                
                for policy in policies:
                    policy_arn = policy["Arn"]
                    
                    # Skip checking specific policy if not the requested one
                    if resource_id and policy["PolicyName"] != resource_id:
                        continue
                        
                    # Get the default version of the policy
                    policy_version = iam.get_policy(PolicyArn=policy_arn)["Policy"]["DefaultVersionId"]
                    policy_doc = iam.get_policy_version(
                        PolicyArn=policy_arn,
                        VersionId=policy_version
                    )["PolicyVersion"]["Document"]
                    
                    # Check for "Effect": "Allow", "Action": "*", "Resource": "*"
                    for statement in policy_doc.get("Statement", []):
                        if (statement.get("Effect") == "Allow" and 
                            statement.get("Action") == "*" and 
                            statement.get("Resource") == "*"):
                            overly_permissive_policies.append(policy["PolicyName"])
                            break
                
                compliance_results["policies"] = {
                    "compliant": len(overly_permissive_policies) == 0,
                    "overly_permissive_policies": overly_permissive_policies
                }
                
            return {
                "success": True,
                "output": compliance_results
            }
                
        except Exception as e:
            self.logger.error(f"Error checking IAM compliance: {str(e)}")
            return {
                "success": False,
                "error": f"Error checking IAM compliance: {str(e)}"
            }
    
    def enable_mfa(self, user_name: str, mfa_type: str = "virtual") -> Dict[str, Any]:
        """
        Enable MFA for a specified user
        
        Args:
            user_name: IAM user name
            mfa_type: Type of MFA (virtual or hardware)
            
        Returns:
            Dictionary with operation result
        """
        try:
            session = boto3.session.Session()
            iam = session.client("iam")
            
            if mfa_type == "virtual":
                # Create a virtual MFA device
                response = iam.create_virtual_mfa_device(
                    VirtualMFADeviceName=f"{user_name}-mfa",
                    Path="/mfa/"
                )
                
                serial_number = response["VirtualMFADevice"]["SerialNumber"]
                qr_code_png = response["VirtualMFADevice"]["QRCodePNG"]
                
                return {
                    "success": True,
                    "output": {
                        "user_name": user_name,
                        "serial_number": serial_number,
                        "qr_code_png": qr_code_png,
                        "instructions": "Please configure this virtual MFA device in your authenticator app, then call enable_mfa_completion with two consecutive authentication codes."
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"MFA type {mfa_type} not yet implemented"
                }
                
        except ClientError as e:
            self.logger.error(f"Error enabling MFA for user {user_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Error enabling MFA for user {user_name}: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error enabling MFA for user {user_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error enabling MFA for user {user_name}: {str(e)}"
            }
    
    def rotate_credentials(self, user_name: str, credential_type: str) -> Dict[str, Any]:
        """
        Rotate IAM user credentials
        
        Args:
            user_name: IAM user name
            credential_type: Type of credential to rotate (access_key, password)
            
        Returns:
            Dictionary with operation result
        """
        try:
            session = boto3.session.Session()
            iam = session.client("iam")
            
            if credential_type == "access_key":
                # List existing access keys
                response = iam.list_access_keys(UserName=user_name)
                existing_keys = response["AccessKeyMetadata"]
                
                if len(existing_keys) >= 2:
                    # User already has maximum number of access keys
                    return {
                        "success": False,
                        "error": "User already has maximum number of access keys (2). Delete an existing key first."
                    }
                
                # Create new access key
                new_key = iam.create_access_key(UserName=user_name)["AccessKey"]
                
                return {
                    "success": True,
                    "output": {
                        "user_name": user_name,
                        "new_access_key_id": new_key["AccessKeyId"],
                        "new_secret_access_key": new_key["SecretAccessKey"],
                        "instructions": "Store these credentials securely. The secret key won't be shown again."
                    }
                }
                
            elif credential_type == "password":
                # Generate a secure random password
                import secrets
                import string
                alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-+=<>?"
                password = ''.join(secrets.choice(alphabet) for _ in range(16))
                
                # Update login profile
                iam.update_login_profile(
                    UserName=user_name,
                    Password=password,
                    PasswordResetRequired=True
                )
                
                return {
                    "success": True,
                    "output": {
                        "user_name": user_name,
                        "new_password": password,
                        "instructions": "Password reset is required on next login. Store this password securely."
                    }
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Invalid credential type: {credential_type}. Must be one of: access_key, password"
                }
                
        except ClientError as e:
            self.logger.error(f"Error rotating credentials for user {user_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Error rotating credentials for user {user_name}: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"Unexpected error rotating credentials for user {user_name}: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error rotating credentials for user {user_name}: {str(e)}"
            }
    
    def check_permissions(self) -> Dict[str, Any]:
        """
        Check if the caller has the necessary permissions for IAM operations
        
        Returns:
            Dictionary with permissions check results
        """
        try:
            session = boto3.session.Session()
            iam = session.client("iam")
            sts = session.client("sts")
            
            # Get current identity
            identity = sts.get_caller_identity()
            
            # Define IAM actions to check
            actions = [
                "iam:CreateUser",
                "iam:DeleteUser",
                "iam:ListUsers",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:ListRoles",
                "iam:CreatePolicy",
                "iam:DeletePolicy",
                "iam:ListPolicies",
                "iam:CreateGroup",
                "iam:DeleteGroup",
                "iam:ListGroups",
                "iam:GetAccountPasswordPolicy",
                "iam:UpdateAccountPasswordPolicy"
            ]
            
            # Check permissions using IAM policy simulator
            # Note: This requires additional permissions, so we'll catch and handle errors
            allowed_actions = []
            denied_actions = []
            
            try:
                for action in actions:
                    try:
                        iam.simulate_principal_policy(
                            PolicySourceArn=identity["Arn"],
                            ActionNames=[action],
                            ResourceArns=["*"],
                            ContextEntries=[]
                        )
                        allowed_actions.append(action)
                    except ClientError:
                        denied_actions.append(action)
            except ClientError:
                # If policy simulation fails, try a more basic approach
                return {
                    "success": True,
                    "output": {
                        "identity": identity,
                        "warning": "Could not perform detailed permission analysis. Please check your IAM permissions."
                    }
                }
            
            return {
                "success": True,
                "output": {
                    "identity": identity,
                    "allowed_actions": allowed_actions,
                    "denied_actions": denied_actions
                }
            }
                
        except Exception as e:
            self.logger.error(f"Error checking IAM permissions: {str(e)}")
            return {
                "success": False,
                "error": f"Error checking IAM permissions: {str(e)}"
            } 