# 🔧 Troubleshooting Guide

## Table of Contents
- [Quick Diagnostics](#quick-diagnostics)
- [Common Issues](#common-issues)
- [Component-Specific Troubleshooting](#component-specific-troubleshooting)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Monitoring & Debugging](#monitoring--debugging)
- [Emergency Procedures](#emergency-procedures)

---

## Quick Diagnostics

Run the following health check script to quickly verify the status of your system components:

```bash
bash health-check.sh

```
---

This checks:

- API Gateway availability
- Lambda function status
- DynamoDB table state
- CloudFront distribution status
- Active CloudWatch alarms

---

## Common Issues
### 1. CORS Errors

- Symptoms: Browser console errors (blocked by CORS policy).
- Fix: Add proper CORS headers in API Gateway or Lambda response.

### 2. Lambda Timeout Errors

- Symptoms: API Gateway returns 504.
- Fixes:

- Increase Lambda timeout to 30s.
- Optimize DB connections (reuse client outside handler).
- Enable provisioned concurrency for critical functions.

### 3. DynamoDB Throttling

- Symptoms: ProvisionedThroughputExceededException.
- Fixes:

- Switch table to on-demand mode.
- Increase read/write capacity.
- Use exponential backoff retries in code.

### 4. CloudFront Serving Stale Content

- Symptoms: Old frontend version still loads.
- Fixes:

- Create cache invalidations.
- Use versioned filenames (e.g., main.123abc.js).
- Adjust TTL for development.

---

# 🔧 Troubleshooting Guide - Quick Reference

## Common Issues

### 1. CORS Errors

**Symptoms:** 
- Browser console errors (blocked by CORS policy)

**Fix:** 
- Add proper CORS headers in API Gateway or Lambda response

---

### 2. Lambda Timeout Errors

**Symptoms:** 
- API Gateway returns 504

**Fixes:**
- Increase Lambda timeout to 30s
- Optimize DB connections (reuse client outside handler)
- Enable provisioned concurrency for critical functions

---

### 3. DynamoDB Throttling

**Symptoms:** 
- `ProvisionedThroughputExceededException`

**Fixes:**
- Switch table to on-demand mode
- Increase read/write capacity
- Use exponential backoff retries in code

---
## Performance Issues

### Diagnosis Checklist

1. CloudFront Cache Hit Ratio
2. Lambda Duration (avg & p99)
3. DynamoDB Latency (PutItem, Query)
4. API Gateway Latency

### Optimizations

- Enable gzip/brotli compression in CloudFront
- Use Query instead of Scan in DynamoDB
- Add caching layer for analytics (60s TTL)

---

## Security Issues

### Exposed S3 Bucket

- Ensure **Block Public Access** is enabled
- Use CloudFront OAI for secure bucket access

### Over-Permissive IAM Roles

- Review IAM policies
- Apply least-privilege principle

---

## Monitoring & Debugging

- Enable **X-Ray tracing** for Lambda & API Gateway
- Use **structured JSON logging** for debugging and metrics

---

## Emergency Procedures

### Full Rollback

```bash
./emergency-rollback.sh
```

This reverts:
- Lambda to previous version
- Frontend to last backup in S3
- Invalidates CloudFront cache

---

<div align="center">
<sub>⚡ Troubleshooting Guide v1.0 | Last Updated: Oct 2025</sub>
</div>