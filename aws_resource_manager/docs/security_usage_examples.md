# AWS Resource Manager Security Usage Examples

This document provides examples of how to use the security features of the AWS Resource Manager
to secure SecureWave's PaymentFlow system in accordance with PCI-DSS requirements.

## Table of Contents

1. [Setting Up Secure IAM Resources](#setting-up-secure-iam-resources)
2. [Enforcing PCI-DSS Compliance](#enforcing-pci-dss-compliance)
3. [Security Auditing and Reporting](#security-auditing-and-reporting)
4. [Automating Security Controls](#automating-security-controls)

## Setting Up Secure IAM Resources

### Creating a Secure Payment Processing Role

```bash
# Create a payment processing role with least privilege permissions
python aws_resource_manager.py create iam role --template secure_role_template \
  --parameters RoleName=payment-processor-role

# Verify the role has been created with proper permissions
python aws_resource_manager.py describe iam role payment-processor-role
```

### Creating a PCI-DSS Compliance Policy

```bash
# Create a PCI-DSS compliance policy
python aws_resource_manager.py create iam policy --template pci_compliance_policy \
  --parameters PolicyName=pci-dss-enforcement

# Attach the policy to multiple roles
python aws_resource_manager.py attach_policy --policy-name pci-dss-enforcement \
  --role-name payment-processor-role
```

### Securing User Access

```bash
# Create a secure user account for payment processing
python aws_resource_manager.py create iam user --resource_name payment-admin \
  --parameters CreateAccessKey=false ConsoleAccess=true Groups=["PaymentAdmins"]

# Enable MFA for a user
python aws_resource_manager.py iam enable_mfa --user_name payment-admin
```

## Enforcing PCI-DSS Compliance

### Account Password Policy

```bash
# Set a PCI-DSS compliant password policy
python aws_resource_manager.py iam set_password_policy \
  --min-length 12 \
  --require-symbols \
  --require-numbers \
  --require-uppercase \
  --require-lowercase \
  --max-age 90 \
  --prevent-reuse 24
```

### Encrypt Sensitive Data

```bash
# Create a KMS key for payment data encryption
python aws_resource_manager.py create kms key \
  --parameters Description="Key for payment data encryption" \
  --parameters EnableKeyRotation=true

# Tag the key appropriately
python aws_resource_manager.py tag resource --resource-arn <kms-key-arn> \
  --tags Application=PaymentFlow Environment=production Compliance=PCI-DSS
```

### Network Security

```bash
# Create a security group that enforces PCI-DSS network segmentation
python aws_resource_manager.py create ec2 security-group \
  --parameters GroupName=payment-processor-sg \
  --parameters Description="Security group for payment processors" \
  --parameters VpcId=<vpc-id>

# Add ingress rule for TLS only
python aws_resource_manager.py ec2 authorize-security-group-ingress \
  --group-id <sg-id> \
  --protocol tcp \
  --port 443 \
  --source <source-cidr>
```

## Security Auditing and Reporting

### PCI-DSS Compliance Checks

```bash
# Check IAM compliance with PCI-DSS
python aws_resource_manager.py check_compliance iam --standard pci-dss

# Check specific policy compliance
python aws_resource_manager.py check_compliance iam --resource-type policy \
  --resource-id payment-flow-policy

# Generate a compliance report
python aws_resource_manager.py check_compliance iam --output-format csv \
  --report-file pci-dss-report.csv
```

### Continuous Security Monitoring

```bash
# Set up a scheduled compliance check (run daily)
0 0 * * * python aws_resource_manager.py check_compliance iam \
  --output-format json --report-file /var/log/compliance/iam-$(date +\%Y\%m\%d).json

# Set up alerting for non-compliant resources
python aws_resource_manager.py monitor compliance \
  --service iam \
  --alert-on-failure \
  --notification-arn <sns-topic-arn>
```

## Automating Security Controls

### Automated Credential Rotation

```bash
# Schedule access key rotation
python aws_resource_manager.py iam schedule_rotation \
  --resource-type access_key \
  --frequency 90days \
  --notification-days 7,3,1

# Immediately rotate credentials
python aws_resource_manager.py iam rotate_credentials \
  --user-name payment-admin \
  --credential-type access_key
```

### Enforcing MFA

```bash
# Enforce MFA across all IAM users
python aws_resource_manager.py iam enforce_mfa --all-users

# Get MFA enforcement report
python aws_resource_manager.py iam mfa_report --output-format rich
```

### Remediating Non-compliant Resources

```bash
# Automatically remediate common issues
python aws_resource_manager.py auto_remediate \
  --service iam \
  --issue-type overly_permissive_policies \
  --dry-run

# Fix specific issue
python aws_resource_manager.py iam fix_permission \
  --policy-name too-permissive-policy \
  --action remove_wildcard_permissions
```

## Resource Deployment with Security Controls

Here's an example of how to deploy the entire PaymentFlow infrastructure with proper security controls:

```bash
# Create a secure deployment file
python aws_resource_manager.py batch_create --file paymentflow-secure-deployment.yaml

# Contents of paymentflow-secure-deployment.yaml:
#
# resources:
#   - service: kms
#     resource_type: key
#     parameters:
#       Description: "Key for payment data encryption"
#       EnableKeyRotation: true
#       Tags:
#         Application: PaymentFlow
#         Compliance: PCI-DSS
#
#   - service: iam
#     resource_type: role
#     template: secure_role_template
#     parameters:
#       RoleName: payment-processor-role
#
#   - service: iam
#     resource_type: policy
#     template: pci_compliance_policy
#     parameters:
#       PolicyName: pci-dss-enforcement
#
#   - service: ec2
#     resource_type: instance
#     parameters:
#       ImageId: ami-12345678
#       InstanceType: t3.medium
#       SubnetId: subnet-12345678
#       SecurityGroupIds: ["sg-12345678"]
#       IamInstanceProfile: payment-processor-role
#       Tags:
#         Name: payment-processor
#         Application: PaymentFlow
#         Environment: production
#         Compliance: PCI-DSS
```

## Best Practices for SecureWave's PaymentFlow

1. **Least Privilege**: Always use the `secure_role_template` when creating roles for payment processing
2. **Encryption**: Ensure all S3 buckets used for PaymentFlow have encryption enabled
3. **MFA**: Require MFA for all users with access to payment data
4. **Audit Logging**: Enable CloudTrail and CloudWatch logging for all payment processing resources
5. **Regular Audits**: Run `check_compliance` at least weekly to identify and fix issues
6. **Credential Rotation**: Schedule regular rotation of all credentials
7. **Network Segmentation**: Keep payment processing resources in a dedicated subnet with strict security group rules
8. **Automated Remediation**: Set up auto-remediation for common security issues

For more information on securing AWS resources for PCI-DSS compliance, see the [AWS PCI-DSS Compliance Guide](https://d1.awsstatic.com/whitepapers/compliance/pci-dss-compliance-on-aws.pdf).
