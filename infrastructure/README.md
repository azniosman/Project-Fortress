# Infrastructure Setup

This directory contains the infrastructure as code (IaC) for Project Fortress using AWS CloudFormation.

## Directory Structure

```
infrastructure/
├── cloudformation/
│   └── base-stack.yml      # Base infrastructure stack
└── scripts/
    └── deploy.sh           # Deployment script
```

## Prerequisites

1. AWS CLI installed and configured
2. Appropriate AWS credentials with necessary permissions
3. AWS region set to `us-east-1` (N. Virginia)

## Deployment

### Base Infrastructure

The base infrastructure includes:
- VPC with public and private subnets
- Internet Gateway
- Route Tables
- ECR Repository
- Security Groups

To deploy the base infrastructure:

```bash
# Deploy to dev environment
./infrastructure/scripts/deploy.sh dev

# Deploy to staging environment
./infrastructure/scripts/deploy.sh staging

# Deploy to production environment
./infrastructure/scripts/deploy.sh prod
```

## Stack Outputs

After deployment, the stack will output the following resources:
- VPC ID
- Public Subnet ID
- Private Subnet ID
- ECR Repository URI
- Security Group ID

## Security Considerations

1. The VPC is configured with:
   - Public subnets for load balancers
   - Private subnets for application servers
   - Security groups with least privilege access

2. ECR Repository is configured with:
   - Image scanning enabled
   - Immutable tags
   - AES256 encryption

## Maintenance

### Updating the Stack

To update the infrastructure:

1. Modify the CloudFormation template
2. Run the deployment script again
3. The script will automatically detect if it needs to create or update the stack

### Deleting the Stack

To delete the stack:

```bash
aws cloudformation delete-stack \
    --stack-name project-fortress-base-${ENVIRONMENT} \
    --region us-east-1
```

## Best Practices

1. Always deploy to dev environment first
2. Review CloudFormation changes before deploying to production
3. Monitor stack events during deployment
4. Keep track of stack outputs for reference
5. Use version control for all infrastructure changes 