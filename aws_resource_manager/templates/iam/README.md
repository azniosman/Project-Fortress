# IAM Templates for SecureWave's PaymentFlow

This directory contains IAM templates specifically designed for SecureWave's PaymentFlow application, with a focus on PCI-DSS compliance and security best practices.

## Available Templates

### 1. Secure Payment Processing Role (`secure_role_template.yaml`)

A least-privilege IAM role template for services processing payment data. This template:

- Grants minimal required permissions for payment processing functions
- Enforces encryption for all data operations
- Ensures secure transport for network communications
- Explicitly denies public access to resources
- Includes PCI-DSS compliance validations and checks

**PCI-DSS Requirements Addressed:**

- Requirement 7.1: Restrict access to system components and cardholder data
- Requirement 7.2: Establish an access control system with least privilege
- Requirement 3.4: Render PAN unreadable anywhere it is stored
- Requirement 4.1: Use strong cryptography and security protocols

**Example Usage:**

```bash
python aws_resource_manager.py create iam role --template secure_role_template \
  --parameters RoleName=payment-api-role
```

### 2. PCI-DSS Compliance Policy (`pci_compliance_policy.yaml`)

An IAM policy template that enforces PCI-DSS controls across AWS resources. This policy:

- Enforces MFA for sensitive operations
- Requires encryption for data at rest
- Enforces secure transport for all communications
- Prevents public access to resources
- Enforces security monitoring and audit logging

**PCI-DSS Requirements Addressed:**

- Requirement 8.3: Secure administrative access with MFA
- Requirement 3.4: Render PAN unreadable anywhere it is stored
- Requirement 4.1: Use strong cryptography for transmission
- Requirement 1.3: Prohibit direct public access to cardholder data environment
- Requirement 10.2: Implement automated audit trails
- Requirement 11.5: Deploy change-detection mechanisms

**Example Usage:**

```bash
python aws_resource_manager.py create iam policy --template pci_compliance_policy \
  --parameters PolicyName=payment-system-pci-controls
```

## Best Practices for Template Usage

1. **Customization**: Always review and customize templates for your specific application needs
2. **Version Control**: Store customized templates in version control
3. **Regular Updates**: Review templates regularly against the latest PCI-DSS requirements
4. **Documentation**: Document any modifications to standard templates
5. **Testing**: Test templates in a non-production environment before deployment
6. **Compliance Checking**: Regularly verify deployed resources against templates for drift

## Template Structure

All templates follow a standard format:

```yaml
name: template_name
description: 'Template description'
resource_type: resource_type
version: 1.0

parameters:
  # Parameters with descriptions and defaults

policy_document:
  # IAM policy document for the resource

validation:
  # Validation rules for template parameters

dependencies:
  # Resource dependencies

security_checks:
  # Security validations specific to PCI-DSS
```

## Adding New Templates

When adding new templates, ensure they:

1. Follow the naming convention `<purpose>_template.yaml`
2. Include detailed descriptions and parameter documentation
3. Implement relevant security checks
4. Map to specific PCI-DSS requirements
5. Follow least privilege principles

## Compliance Verification

After deploying resources using these templates, verify compliance with:

```bash
python aws_resource_manager.py check_compliance iam --standard pci-dss
```
