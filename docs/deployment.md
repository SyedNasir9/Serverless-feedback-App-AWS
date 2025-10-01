# 🚀 Deployment Guide

## Table of Contents
- [Prerequisites](#prerequisites)
- [Initial Setup](#initial-setup)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Monitoring Setup](#monitoring-setup)
- [CI/CD Pipeline](#cicd-pipeline)
- [Post-Deployment Verification](#post-deployment-verification)
- [Rollback Procedures](#rollback-procedures)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **AWS CLI** | 2.x+ | AWS resource management | [Install Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |
| **Node.js** | 18.x+ | Frontend build | [Download](https://nodejs.org/) |
| **Python** | 3.9+ | Lambda functions | [Download](https://python.org/) |
| **Git** | 2.x+ | Version control | [Download](https://git-scm.com/) |
| **npm/yarn** | Latest | Package management | Included with Node.js |

### AWS Account Requirements

- **IAM Permissions:** Administrator or equivalent permissions for:
  - Lambda, API Gateway, DynamoDB, S3, CloudFront
  - CloudWatch, SNS, IAM
  - CloudFormation (if using IaC)
- **Service Limits:**
  - Lambda concurrent executions: 1000+
  - DynamoDB tables: 256+
  - API Gateway APIs: 600+

### Cost Estimate

**Initial Setup:** ~$0 (within free tier)  
**Monthly Running Cost:** $30-$100 (depending on traffic)

---

## Initial Setup

### 1. Clone Repository


git clone https://github.com/yourusername/serverless-feedback-platform.git
cd serverless-feedback-platform
### 2. Configure AWS Credentials

aws configure
aws sts get-caller-identity

### 3. Set Environment Variables
### Create a .env file:

AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
PROJECT_NAME=feedback-platform
ENVIRONMENT=prod
FEEDBACK_TABLE_NAME=feedback-prod
ANALYTICS_TABLE_NAME=analytics-prod
FRONTEND_BUCKET=feedback-frontend-prod
LAMBDA_DEPLOYMENT_BUCKET=lambda-deployments-prod
API_GATEWAY_NAME=feedback-api-prod
CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:feedback-alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

### 4. Install Dependencies
### Frontend:
cd frontend
npm install

### Backend:
cd backend
pip install -r requirements.txt -t ./package

---

### Backend Deployment

### 1. Create DynamoDB Tables
- aws dynamodb create-table --table-name feedback-prod ...
- aws dynamodb create-table --table-name analytics-prod ...
- aws dynamodb wait table-exists --table-name feedback-prod
- aws dynamodb wait table-exists --table-name analytics-prod

---

Initialize Analytics Table:
- aws dynamodb put-item --table-name analytics-prod --item '{...}'

### 2. Create IAM Roles
- Create Lambda execution roles and attach policies for each function.

### 3. Deploy Lambda Functions
- cd backend/functions/create-feedback
- zip -r function.zip . -x "*.git*" "*.pyc" "__pycache__/*"
- aws lambda create-function --function-name create-feedback ...
- Deploy All Functions Script: deploy-lambdas.sh

#!/bin/bash
FUNCTIONS=("create-feedback" "list-feedback" "get-analytics" "stream-aggregator" "rollback-orchestrator")
for func in "${FUNCTIONS[@]}"; do
  ...
done

### 4. Setup DynamoDB Streams Trigger
- STREAM_ARN=$(aws dynamodb describe-table --table-name feedback-prod --query 'Table.LatestStreamArn' --output text)
- aws lambda create-event-source-mapping --function-name stream-aggregator --event-source-arn $STREAM_ARN ...

### 5. Create API Gateway
- Script: setup-api-gateway.sh

source .env
API_ID=$(aws apigateway create-rest-api --name ${API_GATEWAY_NAME} ...)

---

### Frontend Deployment

### 1. Build Frontend
- cd frontend
- npm run build

### 2. Create S3 Bucket

- aws s3 mb s3://feedback-frontend-prod --region us-east-1
- aws s3api put-public-access-block --bucket feedback-frontend-prod ...
- aws s3api put-bucket-versioning --bucket feedback-frontend-prod --versioning-configuration Status=Enabled
- aws s3api put-bucket-encryption --bucket feedback-frontend-prod ...

### 3. CloudFront Distribution
- OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity ...)
- aws s3api put-bucket-policy --bucket feedback-frontend-prod --policy file://bucket-policy.json
- DIST_ID=$(aws cloudfront create-distribution --distribution-config file://cloudfront-config.json ...)

### 4. Upload Frontend to S3
- aws s3 sync build/ s3://feedback-frontend-prod/ --delete ...
- aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
- Deployment Script: frontend/scripts/deploy.sh


- #!/bin/bash
- source ../.env
- npm run build
- aws s3 sync build/ s3://${FRONTEND_BUCKET}/ --delete
- aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} --paths "/*"
- Monitoring Setup
- SNS Topic: Alerts

---

### CloudWatch Metrics & Alarms: 
- Lambda errors, throttling, DynamoDB issues
---

### Rollback Lambda: 
- Subscribed to SNS for automatic rollback

- API_ENDPOINT, FRONTEND_BUCKET, CLOUDFRONT_DISTRIBUTION_ID
---

### Post-Deployment Verification
- Backend Health: curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/health

### Frontend Verification:
- Access via CloudFront URL

### Monitoring Verification: 
- Check CloudWatch logs & alarms

### Rollback Procedures
- Automatic Rollback: Triggered by CloudWatch Alarms

### Manual Rollback: 
- Lambda version alias update and S3 version restore

### Troubleshooting 
Issue	                                Symptoms	                     Solution
CORS errors	                     Browser blocks API calls	        Check API Gateway CORS settings
Lambda timeout	                  504 Gateway Timeout	            Increase Lambda timeout
DynamoDB throttling	400     ProvisionedThroughputExceededException	Switch to on-demand billing
CloudFront stale cache	           Old content served	            Create invalidation
IAM permission denied	            403 Forbidden	                Review IAM policies

<div align="center"> <sub>Deployment Guide v1.0 | Last Updated: October 2025</sub> </div> ```