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

```bash
git clone https://github.com/yourusername/serverless-feedback-platform.git
cd serverless-feedback-platform
```

### 2. Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Verify configuration
aws sts get-caller-identity

# Expected output:
# {
#   "UserId": "AIDAI...",
#   "Account": "123456789012",
#   "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

### 3. Set Environment Variables

Create a `.env` file in the project root:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Project Configuration
PROJECT_NAME=feedback-platform
ENVIRONMENT=prod

# DynamoDB Tables
FEEDBACK_TABLE_NAME=feedback-prod
ANALYTICS_TABLE_NAME=analytics-prod

# S3 Buckets
FRONTEND_BUCKET=feedback-frontend-prod
LAMBDA_DEPLOYMENT_BUCKET=lambda-deployments-prod

# API Gateway
API_GATEWAY_NAME=feedback-api-prod

# CloudFront
CLOUDFRONT_DISTRIBUTION_ID=E1234567890ABC

# Monitoring
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:feedback-alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 4. Install Dependencies

**Frontend:**
```bash
cd frontend
npm install
```

**Backend:**
```bash
cd backend
pip install -r requirements.txt -t ./package
```

---

## Backend Deployment

### Step 1: Create DynamoDB Tables

```bash
# Create Feedback Table
aws dynamodb create-table \
  --table-name feedback-prod \
  --attribute-definitions \
    AttributeName=feedbackId,AttributeType=S \
  --key-schema \
    AttributeName=feedbackId,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE \
  --tags Key=Environment,Value=prod Key=Project,Value=feedback-platform

# Create Analytics Table
aws dynamodb create-table \
  --table-name analytics-prod \
  --attribute-definitions \
    AttributeName=aggregateId,AttributeType=S \
  --key-schema \
    AttributeName=aggregateId,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=10 \
  --tags Key=Environment,Value=prod Key=Project,Value=feedback-platform

# Wait for tables to be active
aws dynamodb wait table-exists --table-name feedback-prod
aws dynamodb wait table-exists --table-name analytics-prod

# Initialize Analytics table with default item
aws dynamodb put-item \
  --table-name analytics-prod \
  --item '{
    "aggregateId": {"S": "global"},
    "totalCount": {"N": "0"},
    "sumRatings": {"N": "0"},
    "positiveCount": {"N": "0"},
    "neutralCount": {"N": "0"},
    "negativeCount": {"N": "0"},
    "lastUpdated": {"S": "2025-01-01T00:00:00Z"}
  }'
```

**Verify Tables:**
```bash
aws dynamodb list-tables
aws dynamodb describe-table --table-name feedback-prod
```

---

### Step 2: Create IAM Roles

**Lambda Execution Role for create-feedback:**

```bash
# Create trust policy
cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name feedback-create-lambda-role \
  --assume-role-policy-document file://trust-policy.json

# Create and attach policy
cat > create-feedback-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:YOUR_ACCOUNT_ID:table/feedback-prod"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:us-east-1:YOUR_ACCOUNT_ID:log-group:/aws/lambda/create-feedback:*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name feedback-create-lambda-role \
  --policy-name create-feedback-policy \
  --policy-document file://create-feedback-policy.json
```

**Repeat for other Lambda functions (list-feedback, get-analytics, stream-aggregator, rollback-orchestrator)**

---

### Step 3: Deploy Lambda Functions

**Package Lambda Function:**

```bash
cd backend/functions/create-feedback

# Create deployment package
zip -r function.zip . -x "*.git*" "*.pyc" "__pycache__/*"

# Upload to S3 (optional, for versioning)
aws s3 cp function.zip s3://lambda-deployments-prod/create-feedback/$(date +%Y%m%d-%H%M%S).zip
```

**Deploy Lambda:**

```bash
# Create function
aws lambda create-function \
  --function-name create-feedback \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/feedback-create-lambda-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 10 \
  --memory-size 256 \
  --environment Variables="{
    FEEDBACK_TABLE_NAME=feedback-prod,
    LOG_LEVEL=INFO
  }" \
  --tags Environment=prod,Project=feedback-platform

# Publish version
aws lambda publish-version \
  --function-name create-feedback \
  --description "Initial production release"

# Create alias
aws lambda create-alias \
  --function-name create-feedback \
  --name prod \
  --function-version 1
```

**Deploy All Functions Script:**

```bash
#!/bin/bash
# deploy-lambdas.sh

FUNCTIONS=("create-feedback" "list-feedback" "get-analytics" "stream-aggregator" "rollback-orchestrator")

for func in "${FUNCTIONS[@]}"; do
  echo "Deploying $func..."
  
  cd backend/functions/$func
  zip -r function.zip . -x "*.git*"
  
  # Update function code
  aws lambda update-function-code \
    --function-name $func \
    --zip-file fileb://function.zip
  
  # Wait for update to complete
  aws lambda wait function-updated --function-name $func
  
  # Publish new version
  VERSION=$(aws lambda publish-version \
    --function-name $func \
    --description "Deployment $(date +%Y%m%d-%H%M%S)" \
    --query 'Version' \
    --output text)
  
  # Update alias
  aws lambda update-alias \
    --function-name $func \
    --name prod \
    --function-version $VERSION
  
  echo "$func deployed successfully (version $VERSION)"
  cd ../../..
done
```

---

### Step 4: Setup DynamoDB Streams Trigger

```bash
# Get Stream ARN
STREAM_ARN=$(aws dynamodb describe-table \
  --table-name feedback-prod \
  --query 'Table.LatestStreamArn' \
  --output text)

# Create event source mapping
aws lambda create-event-source-mapping \
  --function-name stream-aggregator \
  --event-source-arn $STREAM_ARN \
  --starting-position LATEST \
  --batch-size 100 \
  --maximum-batching-window-in-seconds 1
```

---

### Step 5: Create API Gateway

**Using AWS CLI:**

```bash
# Create REST API
API_ID=$(aws apigateway create-rest-api \
  --name feedback-api-prod \
  --description "Feedback Platform API" \
  --endpoint-configuration types=REGIONAL \
  --query 'id' \
  --output text)

echo "API ID: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' \
  --output text)

# Create /feedback resource
FEEDBACK_RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part feedback \
  --query 'id' \
  --output text)

# Create POST method for /feedback
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE \
  --request-parameters method.request.header.Content-Type=true

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:create-feedback:prod/invocations

# Grant API Gateway permission to invoke Lambda
aws lambda add-permission \
  --function-name create-feedback:prod \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:YOUR_ACCOUNT_ID:${API_ID}/*/*/feedback"

# Enable CORS for POST
aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method POST \
  --status-code 200 \
  --response-parameters \
    method.response.header.Access-Control-Allow-Origin=true

aws apigateway put-integration-response \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method POST \
  --status-code 200 \
  --response-parameters \
    method.response.header.Access-Control-Allow-Origin="'*'"

# Add OPTIONS method for CORS preflight
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method OPTIONS \
  --type MOCK \
  --request-templates '{"application/json": "{\"statusCode\": 200}"}'

aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters \
    method.response.header.Access-Control-Allow-Headers=true,\
    method.response.header.Access-Control-Allow-Methods=true,\
    method.response.header.Access-Control-Allow-Origin=true

aws apigateway put-integration-response \
  --rest-api-id $API_ID \
  --resource-id $FEEDBACK_RESOURCE_ID \
  --http-method OPTIONS \
  --status-code 200 \
  --response-parameters \
    method.response.header.Access-Control-Allow-Headers="'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",\
    method.response.header.Access-Control-Allow-Methods="'GET,POST,OPTIONS'",\
    method.response.header.Access-Control-Allow-Origin="'*'"

# Repeat for GET /feedback and GET /analytics...

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --stage-description "Production stage" \
  --description "Initial deployment"

echo "API Endpoint: https://${API_ID}.execute-api.us-east-1.amazonaws.com/prod"
```

**Complete API Setup Script:**

Save as `backend/scripts/setup-api-gateway.sh`:

```bash
#!/bin/bash
set -e

# Load environment variables
source .env

# Create API
API_ID=$(aws apigateway create-rest-api \
  --name ${API_GATEWAY_NAME} \
  --description "Feedback Platform REST API" \
  --endpoint-configuration types=REGIONAL \
  --query 'id' \
  --output text)

echo "Created API: $API_ID"

# Get root resource
ROOT_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' \
  --output text)

# Function to create resource
create_resource() {
  local path=$1
  aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part $path \
    --query 'id' \
    --output text
}

# Function to setup Lambda integration
setup_lambda_integration() {
  local resource_id=$1
  local http_method=$2
  local lambda_function=$3
  
  # Put method
  aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $resource_id \
    --http-method $http_method \
    --authorization-type NONE
  
  # Lambda integration
  aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $resource_id \
    --http-method $http_method \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:${AWS_REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:${lambda_function}:prod/invocations"
  
  # Grant permission
  aws lambda add-permission \
    --function-name ${lambda_function}:prod \
    --statement-id apigateway-${resource_id}-${http_method} \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${AWS_REGION}:${AWS_ACCOUNT_ID}:${API_ID}/*/${http_method}/*" || true
}

# Create resources
FEEDBACK_ID=$(create_resource "feedback")
ANALYTICS_ID=$(create_resource "analytics")
HEALTH_ID=$(create_resource "health")

# Setup endpoints
setup_lambda_integration $FEEDBACK_ID POST create-feedback
setup_lambda_integration $FEEDBACK_ID GET list-feedback
setup_lambda_integration $ANALYTICS_ID GET get-analytics
setup_lambda_integration $HEALTH_ID GET health-check

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --description "Production deployment $(date)"

echo "API deployed successfully!"
echo "Endpoint: https://${API_ID}.execute-api.${AWS_REGION}.amazonaws.com/prod"

# Save API ID to env file
echo "API_GATEWAY_ID=$API_ID" >> .env
```

Run the script:
```bash
chmod +x backend/scripts/setup-api-gateway.sh
./backend/scripts/setup-api-gateway.sh
```

---

## Frontend Deployment

### Step 1: Build Frontend

```bash
cd frontend

# Update API endpoint in .env
cat > .env.production <<EOF
REACT_APP_API_ENDPOINT=https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_REGION=us-east-1
EOF

# Build for production
npm run build

# Verify build
ls -lh build/
```

**Expected output:**
```
build/
├── static/
│   ├── css/
│   ├── js/
│   └── media/
├── index.html
├── favicon.ico
└── manifest.json
```

---

### Step 2: Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://feedback-frontend-prod --region us-east-1

# Block public access (CloudFront will access via OAI)
aws s3api put-public-access-block \
  --bucket feedback-frontend-prod \
  --public-access-block-configuration \
    BlockPublicAcls=true,\
    IgnorePublicAcls=true,\
    BlockPublicPolicy=true,\
    RestrictPublicBuckets=true

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket feedback-frontend-prod \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket feedback-frontend-prod \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

---

### Step 3: Create CloudFront Distribution

**Create Origin Access Identity:**

```bash
# Create OAI
OAI_ID=$(aws cloudfront create-cloud-front-origin-access-identity \
  --cloud-front-origin-access-identity-config \
    CallerReference=$(date +%s),Comment="Feedback Platform OAI" \
  --query 'CloudFrontOriginAccessIdentity.Id' \
  --output text)

echo "OAI ID: $OAI_ID"

# Get OAI canonical user ID
OAI_USER=$(aws cloudfront get-cloud-front-origin-access-identity \
  --id $OAI_ID \
  --query 'CloudFrontOriginAccessIdentity.S3CanonicalUserId' \
  --output text)
```

**Update S3 Bucket Policy:**

```bash
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontOAI",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ${OAI_ID}"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::feedback-frontend-prod/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket feedback-frontend-prod \
  --policy file://bucket-policy.json
```

**Create CloudFront Distribution:**

```bash
cat > cloudfront-config.json <<EOF
{
  "CallerReference": "$(date +%s)",
  "Comment": "Feedback Platform CDN",
  "Enabled": true,
  "DefaultRootObject": "index.html",
  "Origins": {
    "Quantity": 1,
    "Items": [
      {
        "Id": "S3-feedback-frontend",
        "DomainName": "feedback-frontend-prod.s3.amazonaws.com",
        "S3OriginConfig": {
          "OriginAccessIdentity": "origin-access-identity/cloudfront/${OAI_ID}"
        }
      }
    ]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "S3-feedback-frontend",
    "ViewerProtocolPolicy": "redirect-to-https",
    "AllowedMethods": {
      "Quantity": 2,
      "Items": ["GET", "HEAD"],
      "CachedMethods": {
        "Quantity": 2,
        "Items": ["GET", "HEAD"]
      }
    },
    "Compress": true,
    "ForwardedValues": {
      "QueryString": false,
      "Cookies": {
        "Forward": "none"
      }
    },
    "MinTTL": 0,
    "DefaultTTL": 86400,
    "MaxTTL": 31536000
  },
  "CustomErrorResponses": {
    "Quantity": 1,
    "Items": [
      {
        "ErrorCode": 404,
        "ResponsePagePath": "/index.html",
        "ResponseCode": "200",
        "ErrorCachingMinTTL": 300
      }
    ]
  },
  "PriceClass": "PriceClass_100"
}
EOF

# Create distribution
DIST_ID=$(aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json \
  --query 'Distribution.Id' \
  --output text)

echo "CloudFront Distribution ID: $DIST_ID"

# Get CloudFront domain
CLOUDFRONT_DOMAIN=$(aws cloudfront get-distribution \
  --id $DIST_ID \
  --query 'Distribution.DomainName' \
  --output text)

echo "CloudFront Domain: https://${CLOUDFRONT_DOMAIN}"
```

---

### Step 4: Upload Frontend to S3

```bash
# Upload build files
aws s3 sync build/ s3://feedback-frontend-prod/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "*.html" \
  --exclude "*.json"

# Upload HTML with short cache
aws s3 sync build/ s3://feedback-frontend-prod/ \
  --cache-control "public, max-age=0, must-revalidate" \
  --exclude "*" \
  --include "*.html" \
  --include "*.json"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"

echo "Frontend deployed successfully!"
echo "Access your app at: https://${CLOUDFRONT_DOMAIN}"
```

**Deployment Script:**

Save as `frontend/scripts/deploy.sh`:

```bash
#!/bin/bash
set -e

# Load environment
source ../.env

echo "🏗️  Building frontend..."
npm run build

echo "📦 Uploading to S3..."
aws s3 sync build/ s3://${FRONTEND_BUCKET}/ \
  --delete \
  --cache-control "public, max-age=31536000" \
  --exclude "*.html" \
  --exclude "*.json"

aws s3 sync build/ s3://${FRONTEND_BUCKET}/ \
  --cache-control "public, max-age=0, must-revalidate" \
  --exclude "*" \
  --include "*.html" \
  --include "*.json"

echo "🔄 Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --paths "/*" \
  --output text

echo "✅ Deployment complete!"
echo "🌐 URL: https://$(aws cloudfront get-distribution \
  --id ${CLOUDFRONT_DISTRIBUTION_ID} \
  --query 'Distribution.DomainName' \
  --output text)"
```

---

## Monitoring Setup

### Step 1: Create SNS Topic

```bash
# Create SNS topic
TOPIC_ARN=$(aws sns create-topic \
  --name feedback-platform-alerts \
  --query 'TopicArn' \
  --output text)

echo "SNS Topic ARN: $TOPIC_ARN"

# Subscribe email
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol email \
  --notification-endpoint your-email@example.com

# Confirm subscription (check your email)
```

---

### Step 2: Create CloudWatch Metric Filters

```bash
# Metric filter for Lambda errors
aws logs put-metric-filter \
  --log-group-name /aws/lambda/create-feedback \
  --filter-name CreateFeedbackErrors \
  --filter-pattern '[timestamp, request_id, level = ERROR*, ...]' \
  --metric-transformations \
    metricName=CreateFeedbackErrors,\
    metricNamespace=FeedbackPlatform,\
    metricValue=1,\
    defaultValue=0

# Repeat for other Lambda functions
```

---

### Step 3: Create CloudWatch Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name feedback-create-high-errors \
  --alarm-description "Alert when error rate is too high" \
  --metric-name CreateFeedbackErrors \
  --namespace FeedbackPlatform \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions $TOPIC_ARN

# Lambda throttling alarm
aws cloudwatch put-metric-alarm \
  --alarm-name feedback-create-throttles \
  --metric-name Throttles \
  --namespace AWS/Lambda \
  --dimensions Name=FunctionName,Value=create-feedback \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions $TOPIC_ARN

# DynamoDB throttling alarm
aws cloudwatch put-metric-alarm \
  --alarm-name dynamodb-throttled-requests \
  --metric-name UserErrors \
  --namespace AWS/DynamoDB \
  --dimensions Name=TableName,Value=feedback-prod \
  --statistic Sum \
  --period 60 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions $TOPIC_ARN
```

---

### Step 4: Deploy Rollback Lambda

```bash
cd backend/functions/rollback-orchestrator

# Package and deploy
zip -r function.zip .

aws lambda update-function-code \
  --function-name rollback-orchestrator \
  --zip-file fileb://function.zip

# Subscribe to SNS topic
aws sns subscribe \
  --topic-arn $TOPIC_ARN \
  --protocol lambda \
  --notification-endpoint arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:rollback-orchestrator

# Grant SNS permission to invoke Lambda
aws lambda add-permission \
  --function-name rollback-orchestrator \
  --statement-id sns-invoke \
  --action lambda:InvokeFunction \
  --principal sns.amazonaws.com \
  --source-arn $TOPIC_ARN
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-east-1
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.9'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      
      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run frontend tests
        working-directory: ./frontend
        run: npm test
      
      - name: Lint frontend code
        working-directory: ./frontend
        run: npm run lint

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      
      - name: Deploy Lambda functions
        working-directory: ./backend
        run: |
          chmod +x scripts/deploy-lambdas.sh
          ./scripts/deploy-lambdas.sh

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: ${{ env.NODE_VERSION }}
      
      - name: Build frontend
        working-directory: ./frontend
        env:
          REACT_APP_API_ENDPOINT: ${{ secrets.API_ENDPOINT }}
        run: |
          npm ci
          npm run build
      
      - name: Deploy to S3
        working-directory: ./frontend
        run: |
          aws s3 sync build/ s3://${{ secrets.FRONTEND_BUCKET }}/ --delete
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"

  verify:
    needs: [deploy-backend, deploy-frontend]
    runs-on: ubuntu-latest
    steps:
      - name: Health check
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" ${{ secrets.API_ENDPOINT }}/health)
          if [ $response -ne 200 ]; then
            echo "Health check failed with status: $response"
            exit 1
          fi
          echo "Health check passed!"
```

**Required GitHub Secrets:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `API_ENDPOINT`
- `FRONTEND_BUCKET`
- `CLOUDFRONT_DISTRIBUTION_ID`

---

## Post-Deployment Verification

### 1. Backend Health Checks

```bash
# Test API Gateway health endpoint
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/health

# Expected response:
# {"statusCode":200,"message":"Service is healthy","data":{"status":"ok"}}

# Test create feedback
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "rating": 5,
    "message": "Deployment test"
  }'

# Test list feedback
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/feedback

# Test analytics
curl https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/prod/analytics
```

---

### 2. Frontend Verification

```bash
# Check CloudFront distribution status
aws cloudfront get-distribution --id $DIST_ID \
  --query 'Distribution.Status' \
  --output text

# Expected: "Deployed"

# Test frontend access
curl -I https://YOUR_CLOUDFRONT_DOMAIN.cloudfront.net

# Expected: HTTP/2 200
```

---

### 3. Monitoring Verification

```bash
# Check CloudWatch logs
aws logs tail /aws/lambda/create-feedback --follow

# Check alarms
aws cloudwatch describe-alarms \
  --alarm-names feedback-create-high-errors

# Test alarm (intentional failure)
# This should trigger rollback
```

---

## Rollback Procedures

### Automatic Rollback

Automatic rollback is triggered by CloudWatch Alarms when:
- Error rate exceeds threshold (>5 errors in 5 minutes)
- Lambda throttling detected
- DynamoDB issues

**Monitor rollback:**
```bash
# Watch rollback Lambda logs
aws logs tail /aws/lambda/rollback-orchestrator --follow
```

---

### Manual Rollback

**Lambda Function Rollback:**

```bash
# List versions
aws lambda list-versions-by-function \
  --function-name create-feedback \
  --query 'Versions[*].[Version,Description]' \
  --output table

# Update alias to previous version
aws lambda update-alias \
  --function-name create-feedback \
  --name prod \
  --function-version 5  # Previous good version

# Verify
aws lambda get-alias \
  --function-name create-feedback \
  --name prod
```

**Frontend Rollback:**

```bash
# List S3 versions
aws s3api list-object-versions \
  --bucket feedback-frontend-prod \
  --prefix index.html

# Restore previous version
aws s3api copy-object \
  --bucket feedback-frontend-prod \
  --copy-source feedback-frontend-prod/index.html?versionId=PREVIOUS_VERSION_ID \
  --key index.html

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id $DIST_ID \
  --paths "/*"
```

---

## Troubleshooting

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| **CORS errors** | Browser blocks API calls | Check API Gateway CORS settings, ensure OPTIONS method exists |
| **Lambda timeout** | 504 Gateway Timeout | Increase Lambda timeout, optimize code |
| **DynamoDB throttling** | 400 ProvisionedThroughputExceededException | Switch to on-demand billing or increase capacity |
| **CloudFront stale cache** | Old content served | Create invalidation for `/*` |
| **IAM permission denied** | 403 Forbidden | Review and update IAM policies |

### Debug Commands

```bash
# Check Lambda logs
aws logs tail /aws/lambda/FUNCTION_NAME --since 1h

# Check API Gateway execution logs
aws logs tail /aws/apigateway/API_ID/prod --since 1h

# Test Lambda directly
aws lambda invoke \
  --function-name create-feedback \
  --payload '{"body":"{\"name\":\"Test\",\"email\":\"test@example.com\",\"rating\":5,\"message\":\"test\"}"}' \
  response.json

# Check DynamoDB table
aws dynamodb scan \
  --table-name feedback-prod \
  --limit 5
```

---

<div align="center">
<sub>Deployment Guide v1.0 | Last Updated: October 2025</sub>
</div>