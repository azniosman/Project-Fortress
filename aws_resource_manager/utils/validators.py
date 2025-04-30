import boto3
import json
import re
from typing import Dict, Any, List, Union, Optional

def validate_aws_credentials() -> bool:
    """
    Validate that AWS credentials are configured properly.
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    try:
        session = boto3.Session()
        sts = session.client('sts')
        sts.get_caller_identity()
        return True
    except Exception:
        return False

def validate_ec2_instance_type(instance_type: str) -> bool:
    """
    Validate that an EC2 instance type is valid.
    
    Args:
        instance_type: The instance type to validate
        
    Returns:
        bool: True if the instance type is valid, False otherwise
    """
    # Regular expression pattern for EC2 instance types
    pattern = r'^[a-z]+\d+\.[a-z0-9]+$'
    return bool(re.match(pattern, instance_type))

def validate_tags(tags: Dict[str, str]) -> bool:
    """
    Validate that tags are in the correct format.
    
    Args:
        tags: Dictionary of tags
        
    Returns:
        bool: True if the tags are valid, False otherwise
    """
    # Check that all keys and values are strings
    return all(isinstance(k, str) and isinstance(v, str) for k, v in tags.items())

def validate_iam_policy(policy_doc: Union[str, Dict[str, Any]]) -> bool:
    """
    Validate that an IAM policy document is properly formatted.
    
    Args:
        policy_doc: The policy document as a dictionary or JSON string
        
    Returns:
        bool: True if the policy document is valid, False otherwise
    """
    # Convert string to dict if needed
    if isinstance(policy_doc, str):
        try:
            policy_doc = json.loads(policy_doc)
        except json.JSONDecodeError:
            return False
    
    # Validate that it's a dictionary
    if not isinstance(policy_doc, dict):
        return False
    
    # Check for required fields
    if "Version" not in policy_doc or "Statement" not in policy_doc:
        return False
    
    # Validate Version
    if policy_doc["Version"] not in ["2012-10-17", "2008-10-17"]:
        return False
    
    # Validate Statement
    statements = policy_doc["Statement"]
    if not isinstance(statements, list) and not isinstance(statements, dict):
        return False
    
    # Convert single statement to list for consistent handling
    if isinstance(statements, dict):
        statements = [statements]
    
    # Validate each statement
    for statement in statements:
        if not isinstance(statement, dict):
            return False
        
        # Effect is required and must be Allow or Deny
        if "Effect" not in statement or statement["Effect"] not in ["Allow", "Deny"]:
            return False
        
        # Action or NotAction is required
        if "Action" not in statement and "NotAction" not in statement:
            return False
        
        # Resource or NotResource is required
        if "Resource" not in statement and "NotResource" not in statement:
            return False
    
    return True

def validate_policy_for_pci_compliance(policy_doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that an IAM policy meets PCI-DSS compliance requirements.
    
    Args:
        policy_doc: The policy document as a dictionary
        
    Returns:
        Dict with validation results
    """
    issues = []
    warnings = []
    
    # Ensure the policy is valid first
    if not validate_iam_policy(policy_doc):
        return {
            "valid": False,
            "pci_compliant": False,
            "issues": ["Invalid policy document format"]
        }
    
    statements = policy_doc["Statement"]
    if isinstance(statements, dict):
        statements = [statements]
    
    # Check for overly permissive statements (PCI-DSS 7.1.2)
    for i, statement in enumerate(statements):
        # Check for "*" in Action and Resource
        if statement.get("Effect") == "Allow":
            actions = statement.get("Action", [])
            resources = statement.get("Resource", [])
            
            # Convert single values to lists for consistent handling
            if isinstance(actions, str):
                actions = [actions]
            if isinstance(resources, str):
                resources = [resources]
            
            if "*" in actions and "*" in resources:
                issues.append(f"Statement {i} has overly permissive '*' for both Action and Resource")
            elif "*" in actions:
                warnings.append(f"Statement {i} has wildcard Action which may violate least privilege principle")
    
    # Check for encryption requirements (PCI-DSS 3.4)
    s3_put_without_encryption = True
    for statement in statements:
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]
        
        # Look for s3:PutObject operations
        if any("s3:PutObject" in action for action in actions):
            # Check for encryption conditions
            conditions = statement.get("Condition", {})
            encryption_condition = False
            
            # Look for server-side encryption condition
            for condition_type, condition_values in conditions.items():
                if "s3:x-amz-server-side-encryption" in condition_values:
                    encryption_condition = True
                    break
            
            if not encryption_condition:
                s3_put_without_encryption = True
    
    if s3_put_without_encryption:
        warnings.append("S3 PutObject operations may not enforce encryption at rest")
    
    # Check for secure transport (PCI-DSS 4.1)
    secure_transport_enforced = False
    for statement in statements:
        if statement.get("Effect") == "Deny":
            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            
            if "*" in actions or any(action.endswith("*") for action in actions):
                conditions = statement.get("Condition", {})
                for condition_type, condition_values in conditions.items():
                    if "aws:SecureTransport" in condition_values and condition_values["aws:SecureTransport"] == "false":
                        secure_transport_enforced = True
                        break
    
    if not secure_transport_enforced:
        warnings.append("Policy does not enforce secure transport (HTTPS)")
    
    # Evaluate compliance
    is_compliant = len(issues) == 0
    
    return {
        "valid": True,
        "pci_compliant": is_compliant,
        "issues": issues,
        "warnings": warnings
    }

def validate_password_policy_for_pci_compliance(policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that an IAM password policy meets PCI-DSS requirements.
    
    Args:
        policy: The password policy parameters
        
    Returns:
        Dict with validation results
    """
    issues = []
    
    # PCI-DSS requirements for password policies
    pci_requirements = {
        "MinimumPasswordLength": 8,  # PCI-DSS 8.2.3
        "RequireSymbols": True,      # PCI-DSS 8.2.3
        "RequireNumbers": True,      # PCI-DSS 8.2.3
        "RequireUppercaseCharacters": True,  # PCI-DSS 8.2.3
        "RequireLowercaseCharacters": True,  # PCI-DSS 8.2.3
        "MaxPasswordAge": 90,        # PCI-DSS 8.2.4
        "PasswordReusePrevention": 4  # PCI-DSS 8.2.5
    }
    
    # Check each requirement
    if policy.get("MinimumPasswordLength", 0) < pci_requirements["MinimumPasswordLength"]:
        issues.append(f"Password length must be at least {pci_requirements['MinimumPasswordLength']} characters")
    
    if not policy.get("RequireSymbols", False):
        issues.append("Password policy must require symbols")
    
    if not policy.get("RequireNumbers", False):
        issues.append("Password policy must require numbers")
    
    if not policy.get("RequireUppercaseCharacters", False):
        issues.append("Password policy must require uppercase characters")
    
    if not policy.get("RequireLowercaseCharacters", False):
        issues.append("Password policy must require lowercase characters")
    
    if policy.get("MaxPasswordAge", 999) > pci_requirements["MaxPasswordAge"]:
        issues.append(f"Passwords must expire within {pci_requirements['MaxPasswordAge']} days")
    
    if policy.get("PasswordReusePrevention", 0) < pci_requirements["PasswordReusePrevention"]:
        issues.append(f"Password reuse prevention must remember at least {pci_requirements['PasswordReusePrevention']} previous passwords")
    
    return {
        "pci_compliant": len(issues) == 0,
        "issues": issues
    } 