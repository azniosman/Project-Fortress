# AWS Resource Manager

A comprehensive, modular Python script for setting up and managing AWS resources with an interactive command-line interface.

## Overview

AWS Resource Manager provides a user-friendly interface to provision, manage, and monitor AWS resources across multiple services. It is designed with modularity and extensibility in mind, allowing users to easily add support for additional AWS services through a plugin system.

![AWS Resource Manager CLI Interface](images/cli_interface.png)

## Features

### Core Features

- **Modular Architecture**: Separate modules for different AWS services
- **Plugin System**: Easily add new AWS service modules
- **Interactive CLI**: Guided wizards for resource provisioning
- **Resource Lifecycle Management**: Create, update, delete, and monitor resources
- **Dependency Management**: Automatically handle resource dependencies
- **Secure Credential Handling**: Support for AWS IAM roles and secure credential storage
- **Export Capability**: Generate IaC templates (Terraform, CloudFormation, CDK)

### Supported AWS Services

- **Compute**: EC2, Lambda, ECS, Fargate
- **Storage**: S3, EBS, EFS
- **Database**: RDS, DynamoDB, ElastiCache
- **Networking**: VPC, Subnets, Security Groups, Load Balancers
- **Security**: IAM, KMS, Secrets Manager
- **Monitoring**: CloudWatch, X-Ray
- **Serverless**: API Gateway, Step Functions

## Installation

### Prerequisites

- Python 3.8 or higher
- AWS CLI installed and configured
- AWS account with appropriate permissions

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/azniosman/aws-resource-manager.git
   cd aws-resource-manager
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the initial setup:
   ```bash
   python setup.py
   ```

## Quick Start

1. Start the AWS Resource Manager:

   ```bash
   python aws_resource_manager.py
   ```

2. The interactive menu will guide you through the available options.

3. Select a service category (e.g., Compute, Storage, Database).

4. Choose the specific service and operation you want to perform.

5. Follow the interactive prompts to provide necessary configuration information.

## Usage Examples

### Creating an EC2 Instance

```bash
python aws_resource_manager.py create ec2 --guided
```

This will start a wizard that guides you through the process of creating an EC2 instance, including:

- Selecting the AMI
- Choosing the instance type
- Configuring security groups
- Setting up storage
- Configuring monitoring
- Adding tags

### Setting up a VPC with Subnets

```bash
python aws_resource_manager.py create vpc --template basic-vpc
```

This will use a predefined template to create:

- A VPC with the specified CIDR block
- Public and private subnets across multiple availability zones
- Internet Gateway and NAT Gateway
- Route tables and appropriate routes
- Network ACLs

### Creating an S3 Bucket with Policies

```bash
python aws_resource_manager.py create s3 --guided
```

The wizard will guide you through:

- Bucket naming and region selection
- Access control configuration
- Encryption settings
- Lifecycle policies
- Versioning and logging options

## Module Architecture

### Core Modules

- **core/engine.py**: Central orchestration engine
- **core/plugin_manager.py**: Manages service plugins
- **core/config_manager.py**: Handles configuration
- **core/dependency_resolver.py**: Resolves resource dependencies
- **core/state_manager.py**: Manages resource state

### Service Modules

- **modules/compute/**: EC2, Lambda, ECS modules
- **modules/storage/**: S3, EBS, EFS modules
- **modules/database/**: RDS, DynamoDB, ElastiCache modules
- **modules/networking/**: VPC, Subnets, Security Groups modules
- **modules/security/**: IAM, KMS, Secrets Manager modules

### Utility Modules

- **utils/validators.py**: Input validation utilities
- **utils/formatters.py**: Output formatting utilities
- **utils/aws_helpers.py**: AWS API helpers
- **utils/logger.py**: Logging utilities
- **utils/error_handlers.py**: Error handling utilities

## Advanced Usage

### Using Templates

```bash
# List available templates
python aws_resource_manager.py list-templates

# Create resources using a template
python aws_resource_manager.py create --template webapp-stack

# Create a new template from existing resources
python aws_resource_manager.py create-template --name my-webapp --from-resources i-1234abcd, sg-5678efgh
```

### Batch Operations

```bash
# Create multiple resources defined in a YAML file
python aws_resource_manager.py batch-create --file resources.yaml

# Delete multiple resources
python aws_resource_manager.py batch-delete --file resources_to_delete.yaml
```

### Exporting as Infrastructure as Code

```bash
# Export resources as Terraform
python aws_resource_manager.py export --format terraform --output my-terraform-project

# Export as CloudFormation
python aws_resource_manager.py export --format cloudformation --output my-cfn-stack.yaml
```

## Security Best Practices

The AWS Resource Manager implements several security features:

1. **Credential Management**:

   - Never stores AWS credentials in plaintext
   - Supports AWS profile configuration
   - Supports IAM roles and temporary credentials
   - Integrates with AWS Secrets Manager

2. **Resource Security**:

   - Implements AWS security best practices by default
   - Provides compliance checks against CIS benchmarks
   - Validates security group rules and IAM policies

3. **Sensitive Data**:
   - Masks sensitive information in logs and output
   - Encrypts stored configuration and state files
   - Implements secure deletion of temporary files

## Extending the Tool

### Creating a New Service Module

1. Create a new Python file in the appropriate modules directory
2. Implement the `ServiceModule` interface
3. Register the module with the plugin system

Example:

```python
# modules/custom/my_service.py
from core.service_module import ServiceModule

class MyServiceModule(ServiceModule):
    def __init__(self):
        super().__init__("my-service", "My Custom Service")

    def get_operations(self):
        return ["create", "update", "delete", "list"]

    def execute_operation(self, operation, **kwargs):
        # Implement operation logic here
        pass
```

### Adding a New Template

Create a YAML file in the `templates` directory:

```yaml
# templates/my-template.yaml
name: My Template
description: Creates a custom set of resources
resources:
  - type: vpc
    name: main-vpc
    cidr_block: 10.0.0.0/16

  - type: subnet
    name: public-subnet-1
    vpc: ${resources.main-vpc.id}
    cidr_block: 10.0.1.0/24
    public: true

  # Additional resources...
```

## Troubleshooting

### Common Issues

1. **AWS API Throttling**

   - The tool automatically implements exponential backoff
   - You can adjust the backoff settings in config/settings.yaml

2. **Insufficient Permissions**

   - The tool performs permission validation before operations
   - Check AWS IAM policies and roles

3. **Dependency Errors**
   - Use the `--skip-dependency-check` flag to bypass dependency validation
   - Run `python aws_resource_manager.py doctor` to diagnose issues

### Logging

Logs are stored in the `logs` directory with the following log levels:

- `ERROR`: Critical errors that prevent operation
- `WARNING`: Potential issues that don't stop execution
- `INFO`: General operation information
- `DEBUG`: Detailed debugging information

Enable debug logging:

```bash
python aws_resource_manager.py --log-level debug
```

## Contributing

We welcome contributions to the AWS Resource Manager! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
