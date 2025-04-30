# AWS Resource Manager

A comprehensive, modular Python script for setting up and managing AWS resources with an interactive command-line interface.

## Project Overview

AWS Resource Manager provides a user-friendly interface to provision, manage, and monitor AWS resources across multiple services. It is designed with modularity and extensibility in mind, allowing users to easily add support for additional AWS services through a plugin system.

## Key Features

- **Modular Architecture**: Separate modules for different AWS services
- **Plugin System**: Easily add new AWS service modules
- **Interactive CLI**: Guided wizards for resource provisioning
- **Resource Lifecycle Management**: Create, update, delete, and monitor resources
- **Dependency Management**: Automatically handle resource dependencies
- **Secure Credential Handling**: Support for AWS IAM roles and secure credential storage
- **Export Capability**: Generate IaC templates (Terraform, CloudFormation, CDK)

## Project Structure

```
aws_resource_manager/
├── aws_resource_manager.py  # Main entry point
├── README.md                # This file
├── requirements.txt         # Dependencies
├── core/                    # Core modules
│   ├── engine.py            # Central orchestration engine
│   ├── plugin_manager.py    # Manages service plugins
│   ├── config_manager.py    # Handles configuration
│   ├── dependency_resolver.py # Resolves resource dependencies
│   └── interactive_shell.py # Interactive shell for CLI
├── modules/                 # Service modules
│   ├── compute/             # EC2, Lambda, etc.
│   ├── storage/             # S3, EBS, etc.
│   ├── database/            # RDS, DynamoDB, etc.
│   ├── networking/          # VPC, Subnets, etc.
│   └── security/            # IAM, KMS, etc.
├── utils/                   # Utility modules
│   ├── validators.py        # Input validation
│   ├── formatters.py        # Output formatting
│   ├── logger.py            # Logging utilities
│   ├── aws_helpers.py       # AWS API helpers
│   └── error_handlers.py    # Error handling
├── templates/               # Service templates
│   ├── ec2/                 # EC2 templates
│   ├── s3/                  # S3 templates
│   └── ...
├── config/                  # Configuration files
│   └── settings.yaml        # Default settings
└── docs/                    # Documentation
    └── README.md            # Detailed documentation
```

## Getting Started

### Installation

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the AWS Resource Manager: `python aws_resource_manager.py`

### Basic Usage

```bash
# Create an EC2 instance with guided wizard
python aws_resource_manager.py create ec2 --guided

# List all EC2 instances
python aws_resource_manager.py list ec2

# Delete an EC2 instance
python aws_resource_manager.py delete ec2 i-1234567890abcdef0

# Export resources as Terraform
python aws_resource_manager.py export --format terraform
```

### Interactive Shell

For a more interactive experience, you can use the shell mode:

```bash
python aws_resource_manager.py shell
```

This will provide a command-line interface with auto-completion, history, and context-aware help.

## Extending the Tool

The AWS Resource Manager is designed to be easily extended with new service modules. See the detailed documentation for instructions on how to create new service modules and templates.

## Security Features

- **Credential Management**: Secure handling of AWS credentials
- **Input Validation**: Comprehensive validation of all inputs
- **Best Practices**: Implementation of AWS security best practices
- **Encryption**: Support for data encryption at rest and in transit

## Contributing

Contributions are welcome! Please see the Contributing Guide for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
