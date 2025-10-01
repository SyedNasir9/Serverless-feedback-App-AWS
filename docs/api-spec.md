# 📡 Serverless Feedback Platform API Documentation

## Table of Contents
- [Overview](#overview)  
- [Authentication](#authentication)  
- [Base URL](#base-url)  
- [Endpoints](#endpoints)  
  - [Create Feedback](#1-create-feedback)  
  - [List Feedback](#2-list-feedback)  
  - [Get Analytics](#3-get-analytics)  
  - [Health Check](#4-health-check)  
- [Error Handling](#error-handling)  
- [Rate Limiting](#rate-limiting)  
- [Examples](#examples)  
- [Webhooks (Future)](#webhooks-future)  

---

## Overview

The **Serverless Feedback Platform API** provides RESTful endpoints for collecting and retrieving customer feedback. Responses are returned in **JSON** format.  

- **API Version:** v1  
- **Protocol:** HTTPS only  
- **Content-Type:** application/json  

This API enables you to:  
- Submit new feedback  
- Retrieve feedback lists with pagination  
- Get analytics and sentiment insights  
- Monitor API health  

---

## Authentication

**Current:** API Key (in headers)  
**Future:** OAuth 2.0 / JWT via AWS Cognito  

### API Key Authentication

Include your API key in request headers:
X-API-Key: your-api-key-here
Note: For production, enable API Keys through AWS API Gateway Usage Plans.

### Base URL
https://your-api-id.execute-api.us-east-1.amazonaws.com/prod

### Example:
https://abc123def4.execute-api.us-east-1.amazonaws.com/prod
Endpoints

1. Create Feedback
Submit a new customer feedback.

# Endpoint:
POST /feedback
Request Headers:
Content-Type: application/json
X-API-Key: your-api-key (optional)

### Request Body Example:

{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "rating": 5,
  "message": "Great product! Very satisfied with the service."
}
### Request Parameters:

| Parameter | Type    | Required | Default | Description                             |
| --------- | ------- | -------- | ------- | --------------------------------------- |
| limit     | integer | No       | 10      | Number of items to return (1-100)       |
| lastKey   | string  | No       | null    | Pagination token from previous response |


### Response (201 Created):
{
  "statusCode": 201,
  "message": "Feedback created successfully",
  "data": {
    "feedbackId": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "rating": 5,
    "message": "Great product! Very satisfied with the service.",
    "sentiment": "positive",
    "createdAt": "2025-10-01T12:34:56.789Z"
  }
}

2. List Feedback
Retrieve a paginated list of recent feedback entries.

### Endpoint:
GET /feedback
Query Parameters:

| Parameter | Type    | Required | Description          | Constraints        |
| --------- | ------- | -------- | -------------------- | ------------------ |
| name      | string  | Yes      | Customer's full name | 2-100 characters   |
| email     | string  | Yes      | Customer email       | Valid email format |
| rating    | integer | Yes      | Rating score         | 1-5                |
| message   | string  | Yes      | Feedback message     | 10-1000 characters |


Response (200 OK):
{
  "statusCode": 200,
  "message": "Feedback retrieved successfully",
  "data": {
    "items": [ ... ],
    "count": 2,
    "lastKey": "660e8400-e29b-41d4-a716-446655440111"
  }
}

3. Get Analytics
Retrieve aggregated analytics and sentiment insights.

Endpoint:
GET /analytics
Response (200 OK):
{
  "statusCode": 200,
  "message": "Analytics retrieved successfully",
  "data": {
    "totalFeedback": 1234,
    "averageRating": 4.3,
    "sentiment": { "positive": 800, "neutral": 300, "negative": 134 },
    "sentimentPercentage": { "positive": 64.8, "neutral": 24.3, "negative": 10.9 },
    "lastUpdated": "2025-10-01T12:34:56.789Z"
  }
}

4. Health Check
Check API availability.

Endpoint:
GET /health
Response (200 OK):
{
  "statusCode": 200,
  "message": "Service is healthy",
  "data": {
    "status": "ok",
    "timestamp": "2025-10-01T12:34:56.789Z",
    "version": "1.0.0",
    "region": "us-east-1"
  }
}

### Error Handling
Error Response Format:
{
  "statusCode": 400,
  "error": "ValidationError",
  "message": "Invalid input parameters",
  "details": { "field": "email", "issue": "Invalid email format" }
}

### HTTP Status Codes:

200 OK – Request successful
201 Created – Resource created
400 Bad Request – Invalid parameters
401 Unauthorized – Missing/invalid API key
403 Forbidden – Insufficient permissions
404 Not Found – Resource not found
429 Too Many Requests – Rate limit exceeded
500 Internal Server Error – Server-side error

### Rate Limiting

| Tier    | Burst Limit   | Steady-State  | Daily Quota |
| ------- | ------------- | ------------- | ----------- |
| Free    | 100 req/sec   | 500 req/sec   | 10,000      |
| Basic   | 500 req/sec   | 2,000 req/sec | 100,000     |
| Premium | 1,000 req/sec | 5,000 req/sec | 1,000,000   |


### Headers Returned:

X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1633089600

### Best Practices:

Use exponential backoff on 429
Cache responses when possible
Monitor X-RateLimit-Remaining

### Examples

JavaScript (Axios)

const response = await axios.post(`${API_BASE_URL}/feedback`, {
  name: 'John Doe',
  email: 'john@example.com',
  rating: 5,
  message: 'Great product!'
}, { headers: { 'X-API-Key': API_KEY } });

## Python (Requests)

import requests
response = requests.get(f'{API_BASE_URL}/analytics', headers={'X-API-Key': API_KEY})
print(response.json())
Webhooks (Future)
Event	Trigger	Payload
feedback.created	New feedback	Feedback object
feedback.updated	Feedback modified	Updated feedback
analytics.updated	Analytics recalculated	Analytics summary

### Webhook Example:
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-domain.com/webhook",
  "events": ["feedback.created"],
  "secret": "your-webhook-secret"
}

<div align="center"> <sub>API Version 1.0 | Last Updated: October 2025</sub> </div> ```