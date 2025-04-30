# Project Fortress AWS Architecture

```mermaid
graph TB
    subgraph AWS Cloud
        subgraph VPC
            subgraph Public Subnet
                ALB[Application Load Balancer]
            end

            subgraph Private Subnet 1
                EKS[EKS Cluster]
                subgraph EKS Nodes
                    Pod1[Payment API Pod 1]
                    Pod2[Payment API Pod 2]
                    Pod3[Payment API Pod 3]
                end
            end

            subgraph Private Subnet 2
                RDS[(RDS Instance)]
                ElastiCache[(ElastiCache Redis)]
            end

            subgraph Monitoring
                CloudWatch[CloudWatch]
                Prometheus[Prometheus]
                Grafana[Grafana]
            end
        end

        subgraph Security
            WAF[WAF]
            Shield[Shield]
            KMS[KMS]
            IAM[IAM]
            SecretsManager[Secrets Manager]
        end

        subgraph Container Registry
            ECR[ECR Repository]
        end

        subgraph CI/CD
            CodeBuild[CodeBuild]
            CodePipeline[CodePipeline]
        end
    end

    %% Connections
    Internet((Internet)) --> WAF
    WAF --> Shield
    Shield --> ALB

    ALB --> EKS
    EKS --> Pod1
    EKS --> Pod2
    EKS --> Pod3

    Pod1 --> RDS
    Pod2 --> RDS
    Pod3 --> RDS

    Pod1 --> ElastiCache
    Pod2 --> ElastiCache
    Pod3 --> ElastiCache

    Pod1 --> CloudWatch
    Pod2 --> CloudWatch
    Pod3 --> CloudWatch

    CloudWatch --> Prometheus
    Prometheus --> Grafana

    ECR --> CodeBuild
    CodeBuild --> CodePipeline
    CodePipeline --> EKS

    KMS --> RDS
    KMS --> ElastiCache
    KMS --> ECR

    IAM --> EKS
    IAM --> CodeBuild
    IAM --> CodePipeline

    SecretsManager --> Pod1
    SecretsManager --> Pod2
    SecretsManager --> Pod3
```

## AWS Services Description

### Compute & Container

- **EKS (Elastic Kubernetes Service)**
  - Manages containerized applications
  - Auto-scaling enabled
  - 3 replicas of Payment API pods
  - Resource limits: CPU 500m, Memory 512Mi
  - Resource requests: CPU 200m, Memory 256Mi

### Networking

- **VPC with Public and Private Subnets**
  - Public subnet for ALB
  - Private subnets for EKS and databases
  - Security groups with least privilege access
  - VPC Flow Logs enabled

### Load Balancing

- **Application Load Balancer (ALB)**
  - SSL/TLS termination
  - Health checks
  - Path-based routing
  - WAF integration

### Database

- **RDS**
  - Multi-AZ deployment
  - Automated backups
  - Encryption at rest using KMS
  - Enhanced monitoring

### Caching

- **ElastiCache Redis**
  - Session management
  - Rate limiting
  - Cache layer for API responses

### Security

- **WAF (Web Application Firewall)**

  - OWASP rules
  - Rate limiting
  - IP-based access control

- **Shield**

  - DDoS protection
  - Advanced threat protection

- **KMS (Key Management Service)**

  - Encryption key management
  - Key rotation
  - Access control

- **IAM**

  - Role-based access control
  - Least privilege principle
  - Environment-specific roles

- **Secrets Manager**
  - Secure secret storage
  - Automatic rotation
  - Environment-specific secrets

### Monitoring & Logging

- **CloudWatch**

  - Metrics collection
  - Log aggregation
  - Alarm configuration
  - Dashboard creation

- **Prometheus & Grafana**
  - Custom metrics
  - Performance monitoring
  - Custom dashboards

### Container Registry

- **ECR (Elastic Container Registry)**
  - Private repository
  - Image scanning
  - Lifecycle policies
  - Cross-region replication

### CI/CD

- **CodeBuild**

  - Build automation
  - Security scanning
  - Test execution

- **CodePipeline**
  - Deployment automation
  - Environment promotion
  - Approval gates
