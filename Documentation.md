# Project Fortress Documentation

## Repository Information

- **Git Repository**: [https://github.com/azniosman/project-fortress.git](https://github.com/azniosman/project-fortress.git)
- **License**: MIT
- **Primary Branch**: main

## Overview

Project Fortress is a secure payment processing API service deployed on AWS using Kubernetes. The project implements a comprehensive monitoring and logging solution to ensure high availability, security, and observability.

## Architecture

### Infrastructure

- **Cloud Provider**: AWS (us-east-1)
- **Container Orchestration**: Kubernetes
- **Container Runtime**: Docker
- **Load Balancer**: AWS Application Load Balancer

### Components

1. **Payment API Service**

   - Node.js backend application
   - Containerized using Docker
   - Deployed on Kubernetes with 3 replicas
   - Resource limits: CPU 500m, Memory 512Mi
   - Resource requests: CPU 200m, Memory 256Mi

2. **Monitoring Stack**

   - Prometheus for metrics collection
   - Grafana for visualization
   - Node Exporter for system metrics
   - CloudWatch integration for AWS metrics

3. **Logging Stack**
   - AWS CloudWatch Logs
   - Structured JSON logging
   - Log retention: 30 days
   - Centralized log aggregation

## Deployment

### Prerequisites

- AWS CLI configured with appropriate credentials
- kubectl installed and configured
- Docker installed
- Access to AWS ECR or other container registry

### Environment Variables

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
NODE_ENV=production
LOG_LEVEL=info
```

### Deployment Steps

1. **Create Kubernetes Namespace**

```bash
kubectl create namespace fortress
```

2. **Create Grafana Secrets**

```bash
kubectl create secret generic grafana-secrets \
  --namespace fortress \
  --from-literal=admin-password=securewave123
```

3. **Deploy Monitoring Stack**

```bash
kubectl apply -f k8s/monitoring.yaml
```

4. **Deploy Application**

```bash
kubectl apply -f k8s/deployment.yaml
```

5. **Deploy Grafana Dashboard**

```bash
kubectl apply -f k8s/grafana-dashboard.yaml
```

## Monitoring

### Metrics

The following metrics are collected and monitored:

1. **System Metrics**

   - CPU Usage
   - Memory Usage
   - Disk I/O
   - Network I/O

2. **Application Metrics**

   - HTTP Request Rate
   - Response Time
   - Error Rate
   - Active Connections

3. **Business Metrics**
   - Payment Processing Rate
   - Transaction Success Rate
   - Average Transaction Value

### Dashboards

Grafana dashboards are available at:

- Main Dashboard: `http://<grafana-service-ip>:3000`
- Default credentials: admin/securewave123

### Alerts

CloudWatch alarms are configured for:

- High CPU utilization (>80%)
- High Memory utilization (>80%)
- High API latency (>1 second)
- Error rate thresholds

## Logging

### Log Structure

```json
{
  "timestamp": "ISO8601",
  "level": "info|error|warn|debug",
  "message": "Log message",
  "service": "payment-api",
  "environment": "production",
  "traceId": "unique-trace-id",
  "metadata": {
    "requestId": "unique-request-id",
    "userId": "user-id",
    "transactionId": "transaction-id"
  }
}
```

### Log Access

- CloudWatch Logs: `/payment-api/production`
- Log Groups: Organized by date and service
- Log Retention: 30 days

## Security

### Container Security

- Non-root user in containers
- Resource limits and requests
- Security context configurations
- Regular security updates

### Network Security

- Kubernetes network policies
- AWS security groups
- TLS encryption
- API authentication

### Monitoring Security

- Secure Grafana access
- Encrypted metrics storage
- Secure log transmission
- Access control for dashboards

## Maintenance

### Health Checks

- Liveness probe: `/health` endpoint
- Readiness probe: `/health` endpoint
- Probe intervals: 5-10 seconds
- Initial delay: 30 seconds

### Scaling

- Horizontal Pod Autoscaling (HPA)
- Based on CPU and Memory metrics
- Minimum replicas: 3
- Maximum replicas: 10

### Backup

- Grafana dashboards backup
- Prometheus data retention
- Log archival
- Configuration version control

## Troubleshooting

### Common Issues

1. **High CPU Usage**

   - Check application logs
   - Review recent deployments
   - Analyze request patterns
   - Scale resources if needed

2. **High Memory Usage**

   - Check for memory leaks
   - Review garbage collection
   - Analyze heap dumps
   - Adjust memory limits

3. **High Latency**
   - Check network policies
   - Review database performance
   - Analyze request patterns
   - Check external service dependencies

### Debug Tools

- kubectl logs
- kubectl describe
- kubectl exec
- Grafana dashboards
- CloudWatch Logs Insights

## Contributing

1. Fork the repository at [https://github.com/azniosman/project-fortress.git](https://github.com/azniosman/project-fortress.git)
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For detailed contribution guidelines, please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Prerequisites](#prerequisites)
3. [Security Measures](#security-measures)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Deployment Process](#deployment-process)
6. [Infrastructure](#infrastructure)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)
9. [API Documentation](#api-documentation)

## Project Structure

```
project-fortress/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # CI/CD pipeline configuration
├── infrastructure/
│   ├── cloudformation/
│   │   └── base-stack.yml     # Base infrastructure template
│   └── scripts/
│       ├── deploy.py          # Deployment script
│       └── verify_resources.py # Resource verification script
├── src/                       # Application source code
├── tests/                     # Test files
├── .gitignore
├── documentation.md
├── README.md
└── requirements.txt
```

## Prerequisites

### System Requirements

- Python 3.8+
- Node.js 18.x
- AWS CLI v2
- Docker 20.x
- Git

### AWS Requirements

- AWS Account with appropriate permissions
- IAM user with programmatic access
- AWS credentials configured

### Environment Variables

Required environment variables:

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
SNYK_TOKEN=your_snyk_token
SONAR_TOKEN=your_sonar_token
CODECOV_TOKEN=yout_covecov_token
ECR_REGISTRY=
ECR_REPOSITORY=
```

## Security Measures

### Infrastructure Security

- VPC with public and private subnets
- Security groups with least privilege access
- KMS encryption for ECR repositories
- VPC Flow Logs for network monitoring
- Immutable container tags

### Application Security

- CodeQL for static analysis
- Snyk for dependency scanning
- OWASP Dependency Check
- Trivy container scanning
- Automated security testing

### Compliance

- PCI-DSS requirements implemented
- Regular security audits
- Automated compliance checks
- Audit logging enabled

## CI/CD Pipeline

### Pipeline Stages

1. **Security Scanning**

   - CodeQL analysis
   - Dependency vulnerability scanning
   - OWASP checks
   - Security report generation

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
   - ECR repository push
   - Container vulnerability scanning

5. **Deployment**
   - Dev environment deployment
   - Staging environment deployment
   - Production environment deployment

### Environment Configuration

- **Development**

  - URL: https://dev-api.securewave.com
  - Auto-deploy on main branch push
  - Basic security checks

- **Staging**

  - URL: https://staging-api.securewave.com
  - Manual approval required
  - Full security scanning

- **Production**
  - URL: https://api.securewave.com
  - Manual approval required
  - Additional compliance checks

## Deployment Process

### Manual Deployment

1. Clone the repository:

   ```bash
   git clone https://github.com/azniosman/project-fortress.git
   cd project-fortress
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run deployment script:

   ```bash
   python infrastructure/scripts/deploy.py
   ```

4. Follow interactive prompts for environment selection and confirmation.

### Automated Deployment

The CI/CD pipeline automatically handles deployments based on the following triggers:

- Push to main branch
- Pull request creation
- Manual workflow dispatch

## Infrastructure

### CloudFormation Stack

The base infrastructure stack includes:

- VPC with public and private subnets
- Internet Gateway
- Route Tables
- Security Groups
- ECR Repository
- VPC Flow Logs

### Resource Verification

Use the verification script to check resource status:

```bash
python infrastructure/scripts/verify_resources.py
```

## Monitoring and Logging

### CloudWatch Logs

- VPC Flow Logs
- Application logs
- Security event logs

### Monitoring Metrics

- API response times
- Error rates
- Resource utilization
- Security events

## Troubleshooting

### Common Issues

1. **Deployment Failures**

   - Check CloudFormation stack events
   - Verify AWS credentials
   - Ensure sufficient permissions

2. **Security Scan Failures**

   - Review vulnerability reports
   - Update dependencies
   - Check suppression rules

3. **Infrastructure Issues**
   - Verify network configuration
   - Check security group rules
   - Validate IAM permissions

### Debugging Tools

- AWS CloudWatch Logs
- CloudFormation stack events
- GitHub Actions logs
- Security scan reports

## Support

For support, please contact:

- Email: support@securewave.com
- Slack: #project-fortress
- Jira: Project Fortress

## API Documentation

### Payment Processing with Stripe

#### Endpoint: POST /api/v1/payments

Process a payment transaction using Stripe's payment gateway.

##### Prerequisites

- Stripe account (free)
- Stripe API keys (test mode)
- Environment variables configured:
  ```
  STRIPE_SECRET_KEY=sk_test_your_test_key
  ```

##### Test Cards

For testing purposes, use these Stripe test card numbers:

- Success: 4242 4242 4242 4242
- Insufficient Funds: 4000 0000 0000 9995
- Failed Payment: 4000 0000 0000 0002
- Requires Authentication: 4000 0025 0000 3155

##### Request Body

```json
{
  "amount": 100.0,
  "currency": "USD",
  "paymentMethod": "credit_card",
  "cardDetails": {
    "cardNumber": "4242424242424242",
    "expiryDate": "12/25",
    "cvv": "123"
  }
}
```

##### Validation Rules

- **Amount**: Must be a positive number
- **Currency**: Must be one of: USD, EUR, GBP (supported by Stripe)
- **Payment Method**: Must be 'credit_card' (currently supported)
- **Card Details**:
  - Card Number: Must pass Luhn algorithm and Stripe validation
  - Expiry Date: Must be in MM/YY format and not expired
  - CVV: Must be 3-4 digits

##### Rate Limiting

- General limit: 100 requests per 15 minutes per IP
- Failed attempts limit: 5 failed attempts per hour per IP
- Rate limit information in response headers:
  - `RateLimit-Limit`
  - `RateLimit-Remaining`
  - `RateLimit-Reset`

##### Success Response (201 Created)

```json
{
  "success": true,
  "data": {
    "id": "pi_3O1234567890",
    "status": "succeeded",
    "amount": 100.0,
    "currency": "usd"
  }
}
```

##### Error Responses

- **400 Bad Request** (Validation Error):

```json
{
  "success": false,
  "error": "Invalid card number"
}
```

- **402 Payment Required** (Payment Failed):

```json
{
  "success": false,
  "error": "Your card was declined"
}
```

- **429 Too Many Requests** (Rate Limit Exceeded):

```json
{
  "success": false,
  "error": "Too many payment requests, please try again later"
}
```

#### Endpoint: GET /api/v1/payments/:paymentIntentId

Retrieve the status of a payment.

##### Parameters

- `paymentIntentId`: The Stripe Payment Intent ID (e.g., "pi_3O1234567890")

##### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "id": "pi_3O1234567890",
    "status": "succeeded",
    "amount": 100.0,
    "currency": "usd"
  }
}
```

##### Error Response (404 Not Found)

```json
{
  "success": false,
  "error": "Payment not found"
}
```

### Implementation Details

#### Payment Flow

1. Validate request data
2. Create Stripe Payment Method from card details
3. Create and confirm Payment Intent
4. Return payment status and details

#### Security Features

1. **PCI Compliance**

   - Card data never stored
   - Direct integration with Stripe API
   - Secure transmission of card details

2. **Input Validation**

   - Card validation before processing
   - Amount and currency validation
   - Expiry date validation

3. **Rate Limiting**

   - Protection against brute force attempts
   - Separate limits for successful and failed attempts
   - IP-based rate limiting

4. **Error Handling**
   - Detailed error messages in development
   - Sanitized errors in production
   - Comprehensive error logging

#### Testing

To test the payment integration:

1. Use Stripe test API keys
2. Use Stripe test card numbers
3. Monitor payment status in Stripe Dashboard
4. Check logs for detailed information

#### Monitoring

- Payment success/failure rates
- Response times
- Error rates
- Rate limit violations

### Payment Processing

#### Endpoint: POST /api/v1/payments

Process a payment transaction.

##### Request Body

```json
{
  "amount": 100.0,
  "currency": "USD",
  "paymentMethod": "credit_card",
  "cardDetails": {
    "cardNumber": "4111111111111111",
    "expiryDate": "12/25",
    "cvv": "123"
  }
}
```

##### Validation Rules

- **Amount**: Must be a positive number
- **Currency**: Must be one of: USD, EUR, GBP
- **Payment Method**: Must be one of: credit_card, bank_transfer
- **Card Details** (required for credit_card payments):
  - Card Number: Must pass Luhn algorithm validation
  - Expiry Date: Must be in MM/YY format and not expired
  - CVV: Must be 3-4 digits

##### Rate Limiting

- General limit: 100 requests per 15 minutes per IP
- Failed attempts limit: 5 failed attempts per hour per IP
- Rate limit information is provided in response headers:
  - `RateLimit-Limit`: Maximum number of requests allowed
  - `RateLimit-Remaining`: Number of requests remaining
  - `RateLimit-Reset`: Time when the rate limit resets

##### Response Headers

- `RateLimit-Limit`: Maximum number of requests allowed
- `RateLimit-Remaining`: Number of requests remaining
- `RateLimit-Reset`: Time when the rate limit resets

##### Success Response (201 Created)

```json
{
  "success": true,
  "data": {
    "id": "pay_1234567890",
    "status": "completed",
    "amount": 100.0,
    "currency": "USD"
  }
}
```

##### Error Responses

- **400 Bad Request** (Validation Error):

```json
{
  "success": false,
  "error": "Invalid card number"
}
```

- **429 Too Many Requests** (Rate Limit Exceeded):

```json
{
  "success": false,
  "error": "Too many payment requests, please try again later"
}
```

##### Security Features

1. **Input Validation**

   - Comprehensive validation of all input fields
   - Credit card number validation using Luhn algorithm
   - Expiry date validation
   - CVV format validation

2. **Rate Limiting**

   - Two-tier rate limiting system
   - Separate limits for general requests and failed attempts
   - IP-based rate limiting
   - Detailed logging of rate limit violations

3. **Logging**

   - All validation failures are logged
   - Rate limit violations are logged
   - Payment processing events are logged
   - Error details are logged for debugging

4. **Error Handling**
   - Detailed error messages for validation failures
   - Proper HTTP status codes
   - Consistent error response format
   - Secure error messages in production
