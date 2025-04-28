#!/bin/bash

# Exit on error
set -e

# Configuration
STACK_NAME="project-fortress-base"
TEMPLATE_FILE="infrastructure/cloudformation/base-stack.yml"
REGION="us-east-1"
ENVIRONMENT=${1:-"dev"}

# Check if environment is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <environment>"
    echo "Environment options: dev, staging, prod"
    exit 1
fi

# Create the stack
echo "Creating stack: ${STACK_NAME}-${ENVIRONMENT}"
aws cloudformation create-stack \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --template-body "file://${TEMPLATE_FILE}" \
    --parameters \
        ParameterKey=Environment,ParameterValue=${ENVIRONMENT} \
        ParameterKey=VPCCidrBlock,ParameterValue=10.0.0.0/16 \
        ParameterKey=PublicSubnet1CidrBlock,ParameterValue=10.0.1.0/24 \
        ParameterKey=PrivateSubnet1CidrBlock,ParameterValue=10.0.2.0/24 \
    --capabilities CAPABILITY_IAM \
    --region ${REGION}

echo "Waiting for stack creation to complete..."
aws cloudformation wait stack-create-complete \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region ${REGION}

echo "Stack creation completed. Getting outputs..."
aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}-${ENVIRONMENT}" \
    --region ${REGION} \
    --query 'Stacks[0].Outputs' \
    --output table

echo "Deployment completed successfully!" 