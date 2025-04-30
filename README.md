# Project Fortress

A secure payment processing API service deployed on AWS using Kubernetes, implementing comprehensive security measures and DevSecOps practices.

## DevSecOps Pipeline

### Branch Strategy

- `development`: Main development branch, accessible to all developers
- `staging`: Pre-production environment for testing
- `production`: Production environment with strict access controls

### Security Measures

1. **Static Application Security Testing (SAST)**

   - CodeQL analysis for JavaScript and Python
   - SonarQube code quality and security scanning
   - Gitleaks for secret detection
   - Snyk for dependency vulnerability scanning
   - OWASP Dependency Check

2. **Infrastructure Security**

   - CloudFormation template validation
   - cfn-lint for CloudFormation linting
   - Checkov for infrastructure security scanning
   - AWS security best practices enforcement

3. **Container Security**

   - Trivy vulnerability scanning
   - Non-root user in containers
   - Resource limits and requests
   - Security context configurations

4. **Environment Security**
   - Separate AWS credentials for each environment
   - Environment-specific secrets management
   - Strict branch protection rules
   - Required code reviews and approvals

### CI/CD Pipeline Stages

1. **Security Scanning**

   - SAST with CodeQL
   - Dependency vulnerability scanning
   - Secret detection
   - Code quality analysis

2. **Lint and Test**

   - ESLint code quality checks
   - Unit tests with coverage
   - Integration tests

3. **Infrastructure Validation**

   - CloudFormation template validation
   - Security group validation
   - Network configuration checks

4. **Build and Push**

   - Docker image building
   - Container vulnerability scanning
   - ECR repository push

5. **Deployment**
   - Dev environment deployment
   - Staging environment deployment
   - Production environment deployment

## Getting Started

### Prerequisites

- Node.js 18.x
- Python 3.8+
- AWS CLI v2
- Docker 20.x
- Git

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/azniosman/project-fortress.git
   cd project-fortress
   ```

2. Install dependencies:

   ```bash
   npm install
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run development server:
   ```bash
   npm run dev
   ```

## Security

### Secret Management

- All secrets are stored in GitHub Secrets
- Environment-specific secrets are used for deployments
- Gitleaks prevents accidental secret commits
- Regular secret rotation is enforced

### Access Control

- Branch protection rules enforce code review requirements
- Environment-specific deployment permissions
- Required security team approval for production deployments
- Audit logging for all security events

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For detailed contribution guidelines, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please contact:

- Email: support@securewave.com
- Slack: #project-fortress
- Jira: Project Fortress
