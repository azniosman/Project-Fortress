# Project Fortress

A secure deployment pipeline for PaymentFlow API service, implementing DevSecOps best practices.

## Overview

Project Fortress is an initiative to modernize SecureWave's deployment pipeline and enhance the security posture of the PaymentFlow API service. The project involves containerizing the existing Node.js backend application, implementing a comprehensive CI/CD pipeline with integrated security controls, and deploying to AWS using infrastructure as code principles.

## Features

- Secure CloudFormation deployment with interactive menu
- Resource verification and health checks
- Environment-specific configurations (dev, staging, prod)
- Comprehensive error handling and logging
- AWS resource management and monitoring

## Prerequisites

- Python 3.8+
- AWS CLI configured with appropriate credentials
- Boto3 library
- Robo library for CLI interactions

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/azniosman/project-fortress.git
   cd project-fortress
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Deployment

To deploy the infrastructure:

```bash
./infrastructure/scripts/deploy.py
```

The script will:
1. Prompt for environment selection (dev, staging, prod)
2. Validate the CloudFormation template
3. Create or update the stack
4. Display stack outputs upon completion

### Resource Verification

To verify deployed resources:

```bash
./infrastructure/scripts/verify_resources.py
```

The script will:
1. Prompt for environment selection
2. Check the status of all deployed resources
3. Display detailed status information

## Project Structure

```
project-fortress/
├── infrastructure/
│   ├── scripts/
│   │   ├── deploy.py
│   │   └── verify_resources.py
│   └── cloudformation/
│       └── base-stack.yml
├── .gitignore
└── README.md
```

## Security

- All deployments are performed with least privilege principles
- Resources are tagged with environment and project information
- Sensitive information is managed through AWS Parameter Store
- Infrastructure changes are tracked and auditable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
