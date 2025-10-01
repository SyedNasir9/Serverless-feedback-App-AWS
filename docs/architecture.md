# 🏗️ Serverless Feedback Platform Architecture

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Principles](#architecture-principles)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Security](#security)
- [Scalability & Reliability](#scalability--reliability)
- [Future Enhancements](#future-enhancements)

---

## System Overview
The **Serverless Feedback Platform** is built fully on **AWS serverless services** following an **event-driven architecture**.  
It is designed for high availability, automatic scaling, and minimal operational overhead. Users submit feedback via a **React SPA**, which triggers serverless Lambdas to process, store, and analyze feedback in **DynamoDB**. Metrics and logs enable monitoring and automated self-healing.

---

## Architecture Principles
1. **Serverless-First**: No server management, pay-per-use, automatic scaling.  
2. **Event-Driven**: DynamoDB Streams + SNS decouple components.  
3. **Single Responsibility**: Each Lambda has one purpose, promoting maintainability.  
4. **Defense in Depth**: IAM least-privilege, encryption, API Gateway security.  
5. **Observable by Default**: Structured logs, metrics, CloudWatch alarms, auto rollback.  
6. **Cost Optimized**: On-demand pricing, caching, pre-aggregated analytics.

---

## Component Architecture

### Frontend (React SPA)
- **Tech:** React 18, Axios, React Router  
- **Deployment:** S3 + CloudFront (CDN), OAI for secure access  
- **Features:** Responsive design, real-time dashboard, code splitting, offline support

### API Layer (API Gateway)
- **Endpoints:**
  - `POST /feedback` → Create feedback  
  - `GET /feedback` → List feedback  
  - `GET /analytics` → Fetch analytics  
  - `GET /health` → Health check  
- **Security:** API keys, throttling, CORS  
- **Monitoring:** CloudWatch logs + metrics

### Lambda Functions
| Function | Purpose | Memory | Timeout |
|----------|--------|--------|---------|
| create-feedback | Process feedback, sentiment analysis, store in DynamoDB | 256 MB | 10s |
| list-feedback | Paginated retrieval of feedback | 256 MB | 10s |
| get-analytics | Aggregate analytics from DynamoDB | 128 MB | 5s |
| stream-aggregator | Process DynamoDB Streams for analytics | 256 MB | 30s |
| rollback-orchestrator | Auto-rollback via SNS alerts | 256 MB | 60s |

### DynamoDB Tables
- **Feedback Table:** UUID primary key, rating, sentiment, timestamp. Streams enabled.  
- **Analytics Table:** Single global aggregate item. Atomic counters for total, positive, neutral, negative counts.

---

## Data Flow

### Write Path
1. User submits feedback → CloudFront → API Gateway  
2. `create-feedback` Lambda validates + analyzes sentiment → stores in DynamoDB  
3. DynamoDB Stream triggers `stream-aggregator` → updates analytics table  
4. Response returned to user (~120ms), analytics updated asynchronously (~1–2s)

### Read Path
1. User requests analytics → CloudFront → API Gateway  
2. `get-analytics` Lambda fetches single-item aggregate from DynamoDB  
3. Response cached at edge (~10–20ms for repeated requests)

### Auto-Rollback Flow
- CloudWatch detects Lambda errors → SNS → `rollback-orchestrator` Lambda  
- Lambda switches to last good version → notifies team  
- Recovery time: <2 minutes

---

## Security
- **Network:** HTTPS, TLS 1.2+, CloudFront OAI, optional VPC for Lambda  
- **IAM:** Least-privilege per Lambda  
- **Data:** KMS encryption at rest (DynamoDB, S3), TLS in transit  
- **API:** Rate limiting, input validation, API keys, future Cognito auth  
- **Observability:** CloudWatch dashboards, alarms, structured logging

---

## Scalability & Reliability
- **Horizontal:** Lambda concurrency, DynamoDB on-demand, CloudFront global scaling  
- **Vertical:** Lambda memory scales CPU, DynamoDB provisioned RCU/WCU if needed  
- **Backups:** DynamoDB PITR (35-day window), S3 versioning, Lambda code versioning  
- **Recovery:** RTO <15 min, RPO <5 min, automated rollback <2 min  

---

## Future Enhancements
- Blue-green deployments, ML sentiment analysis  
- Multi-region active-active architecture  
- Real-time WebSocket notifications  
- Cognito authentication & RBAC  
- Advanced analytics with AWS Timestream

---

<div align="center">
<sub>Last Updated: Oct 2025 | Version 1.0 (Medium Overview)</sub>
</div>
