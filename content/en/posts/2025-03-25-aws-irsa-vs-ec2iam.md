---
title: IRSA vs. EC2 IAM: Usage Scenarios and Permission Management Practices
date: 2025-03-25T11:53:08+08:00
slug: aws-irsa-vs-ec2iam
categories: 
- Engineering
featured: true
tags:
- AWS
---

In AWS environments, assigning permissions to workloads is critical for security and functionality. For applications running on EC2 or EKS, two common approaches are **EC2 IAM Instance Roles** and **IRSA (IAM Roles for Service Accounts)**. This article explains what they are, their differences, usage scenarios with code examples, and common issues with solutions, helping the team choose the right authentication method and avoid permission confusion.

<!--more-->

## 1. What Are IRSA and EC2 IAM?

### 1.1 EC2 IAM Instance Role

An EC2 IAM Instance Role is an IAM role attached to an EC2 instance. Applications running on the instance retrieve temporary credentials via the Instance Metadata Service (IMDS) to access authorized AWS resources. Its permission scope applies to the entire instance, making it suitable for traditional VM environments.

### 1.2 IRSA (IAM Roles for Service Accounts)

IRSA is an AWS mechanism designed for EKS, linking IAM roles to Kubernetes Service Accounts. This allows Pods in an EKS cluster to obtain independent AWS permissions. IRSA leverages an OIDC (OpenID Connect) identity provider, with applications using the assumeRoleWithWebIdentity API to acquire temporary credentials. A Trust Policy must be configured for the IAM role to establish this trust relationship.

## 2. Differences Between IRSA and EC2 IAM

| **Feature**                | **EC2 IAM Instance Role**                              | **IRSA**                                |
| -------------------------- | ------------------------------------------------------ | --------------------------------------- |
| **Environment**            | EC2 instances (non-containerized or simple containers) | EKS clusters (containerized workloads)  |
| **Permission Granularity** | Entire instance, shared by all processes               | Pod-level, unique per Service Account   |
| **Authentication**         | IMDS for temporary credentials                         | OIDC token + assumeRoleWithWebIdentity  |
| **Complexity**             | Simple, directly attached to instance                  | Requires OIDC provider and Trust Policy |
| **Typical Use Case**       | Monolithic apps, batch jobs                            | Multi-tenant, fine-grained control      |

- **EC2 IAM**: Simple setup for uniform permission needs, less flexible.
- **IRSA**: Flexible for containerized environments, requires Trust Policy for assumeRoleWithWebIdentity.

## 3. Code Examples and Usage Scenarios

### 3.1 EC2 IAM Instance Role

**Scenario**: A script on an EC2 instance needs S3 access.

1. Attach an IAM role (e.g., S3ReadOnlyRole) to the EC2 instance.
2. The script uses AWS SDK directly, no extra configuration needed.

```python
# Python script running on EC2
import boto3
s3 = boto3.client('s3')
buckets = s3.list_buckets()
print(buckets)
```

**Applicability**: All processes share the instance role’s permissions, ideal for monolithic apps.

### 3.2 IRSA

**Scenario**: An EKS Pod needs DynamoDB access.

1. Create an IAM role with a Trust Policy.
2. Bind the role to a Service Account.

**Trust Policy Example**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/oidc.eks.us-west-2.amazonaws.com/id/EXAMPLED539D4635E53D248B"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "oidc.eks.us-west-2.amazonaws.com/id/EXAMPLED539D4635E53D248B:sub": "system:serviceaccount:default:dynamo-access-sa"
        }
      }
    }
  ]
}
```

- Principal: Specifies the EKS cluster’s OIDC provider.
- Action: Permits sts:AssumeRoleWithWebIdentity.
- Condition: Restricts role assumption to the specified Service Account.

**Service Account and Pod Configuration**:

```yaml
# Service Account configuration
apiVersion: v1
kind: ServiceAccount
metadata:
  name: dynamo-access-sa
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/DynamoDBRole

# Pod configuration
apiVersion: v1
kind: Pod
metadata:
  name: dynamo-pod
spec:
  serviceAccountName: dynamo-access-sa
  containers:
  - name: app
    image: my-app:latest
```

**Application Code**:

```python
# Python code running in the Pod
import boto3
dynamodb = boto3.client('dynamodb')
tables = dynamodb.list_tables()
print(tables)
```

**Applicability**: Pods gain independent permissions via assumeRoleWithWebIdentity, perfect for multi-service scenarios.

## 4. Common Issues and Solutions

### 4.1 Issue: Credential Conflict Between EC2 IAM and IRSA

**Description**: On an EKS node (an EC2 instance), applications may use the EC2 IAM role’s credentials instead of IRSA’s. **Symptoms**: Pod API calls fail with AccessDenied, logs show the wrong role ARN. **Solution**:

- Ensure Pod environment variables are set:

  ```
  AWS_ROLE_ARN=arn:aws:iam::123456789012:role/DynamoDBRole
  AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token
  ```

- Limit EC2 IAM role permissions to node essentials (e.g., ECR image pulls).

### 4.2 Issue: Trust Policy Misconfiguration

**Description**: IRSA’s Trust Policy lacks the correct OIDC provider or Service Account, causing assumeRoleWithWebIdentity to fail. **Symptoms**: Errors like InvalidIdentityToken or AccessDenied. **Solution**:

- Verify OIDC provider ARN:

  ```bash
  aws eks describe-cluster --name my-cluster --query "cluster.identity.oidc"
  ```

- Ensure Trust Policy’s sub matches the Service Account name.

### 4.3 Issue: Misusing EC2 IAM Instead of IRSA

**Description**: Relying on EC2 IAM for EKS workloads leads to all Pods sharing permissions, breaching least privilege. **Symptoms**: Over-permissioning, potential security risks. **Solution**:

- Migrate to IRSA with dedicated Trust Policies and roles.

- Verify credential source:

  ```bash
  aws sts get-caller-identity
  ```

## 5. Conclusion

EC2 IAM Instance Roles suit traditional EC2 setups with simple configuration but coarse granularity. IRSA, designed for EKS, offers Pod-level control via Trust Policies and assumeRoleWithWebIdentity. By understanding their scenarios, configuring Trust Policies correctly, and using code examples, the team can prevent permission confusion. Define workload types during deployment, adhere to least privilege, and regularly validate credential sources for secure, efficient operations.

## 6. Reference

+ [**IAM roles for service accounts**](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
+ [IAM roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)

