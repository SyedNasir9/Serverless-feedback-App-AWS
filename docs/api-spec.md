# 📡 API Documentation

## Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL](#base-url)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

---

## Overview

The Serverless Feedback Platform API provides RESTful endpoints for collecting and retrieving customer feedback. All responses are returned in JSON format.

**API Version:** v1  
**Protocol:** HTTPS only  
**Content-Type:** application/json

---

## Authentication

**Current:** API Key (in headers)  
**Future:** OAuth 2.0 / JWT tokens via AWS Cognito

### API Key Authentication

Include your API key in the request headers:

```http
X-API-Key: your-api-key-here
```

**Note:** In the current implementation, API Gateway can be configured with or without authentication. For production, enable API Keys through AWS API Gateway Usage Plans.

---

## Base URL

```
https://your-api-id.execute-api.us-east-1.amazonaws.com/prod
```

Replace `your-api-id` with your actual API Gateway ID.

**Example:**
```
https://abc123def4.execute-api.us-east-1.amazonaws.com/prod
```

---

## Endpoints

### 1. Create Feedback

Submit new customer feedback.

#### **Endpoint**
```http
POST /feedback
```

#### **Request Headers**
```http
Content-Type: application/json
X-API-Key: your-api-key (optional)
```

#### **Request Body**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "rating": 5,
  "message": "Great product! Very satisfied with the service."
}
```

#### **Request Body Parameters**

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| name | string | Yes | Customer's full name | 2-100 characters |
| email | string | Yes | Customer's email address | Valid email format |
| rating | integer | Yes | Rating score | 1-5 (integer) |
| message | string | Yes | Feedback message | 10-1000 characters |

#### **Response**

**Success (201 Created):**
```json
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
```

#### **Example cURL**
```bash
curl -X POST https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/feedback \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "rating": 5,
    "message": "Great product! Very satisfied with the service."
  }'
```

#### **Example JavaScript (Axios)**
```javascript
const axios = require('axios');

const createFeedback = async () => {
  try {
    const response = await axios.post(
      'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/feedback',
      {
        name: 'John Doe',
        email: 'john.doe@example.com',
        rating: 5,
        message: 'Great product! Very satisfied with the service.'
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'your-api-key'
        }
      }
    );
    console.log('Feedback created:', response.data);
  } catch (error) {
    console.error('Error creating feedback:', error.response.data);
  }
};

createFeedback();
```

---

### 2. List Feedback

Retrieve a paginated list of recent feedback entries.

#### **Endpoint**
```http
GET /feedback
```

#### **Request Headers**
```http
X-API-Key: your-api-key (optional)
```

#### **Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| limit | integer | No | 10 | Number of items to return (1-100) |
| lastKey | string | No | null | Pagination token from previous response |

#### **Response**

**Success (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Feedback retrieved successfully",
  "data": {
    "items": [
      {
        "feedbackId": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "rating": 5,
        "message": "Great product!",
        "sentiment": "positive",
        "createdAt": "2025-10-01T12:34:56.789Z"
      },
      {
        "feedbackId": "660e8400-e29b-41d4-a716-446655440111",
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "rating": 3,
        "message": "Could be better.",
        "sentiment": "neutral",
        "createdAt": "2025-10-01T11:20:30.123Z"
      }
    ],
    "count": 2,
    "lastKey": "660e8400-e29b-41d4-a716-446655440111"
  }
}
```

#### **Example cURL**
```bash
curl -X GET "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/feedback?limit=10" \
  -H "X-API-Key: your-api-key"
```

#### **Example JavaScript (Fetch)**
```javascript
const listFeedback = async (limit = 10, lastKey = null) => {
  try {
    let url = `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/feedback?limit=${limit}`;
    if (lastKey) {
      url += `&lastKey=${encodeURIComponent(lastKey)}`;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'X-API-Key': 'your-api-key'
      }
    });

    const data = await response.json();
    console.log('Feedback list:', data);
    return data;
  } catch (error) {
    console.error('Error listing feedback:', error);
  }
};

listFeedback();
```

#### **Pagination Example**
```javascript
// Get first page
const firstPage = await listFeedback(10);

// Get next page using lastKey
if (firstPage.data.lastKey) {
  const secondPage = await listFeedback(10, firstPage.data.lastKey);
}
```

---

### 3. Get Analytics

Retrieve aggregated analytics and sentiment insights.

#### **Endpoint**
```http
GET /analytics
```

#### **Request Headers**
```http
X-API-Key: your-api-key (optional)
```

#### **Response**

**Success (200 OK):**
```json
{
  "statusCode": 200,
  "message": "Analytics retrieved successfully",
  "data": {
    "totalFeedback": 1234,
    "averageRating": 4.3,
    "sentiment": {
      "positive": 800,
      "neutral": 300,
      "negative": 134
    },
    "sentimentPercentage": {
      "positive": 64.8,
      "neutral": 24.3,
      "negative": 10.9
    },
    "lastUpdated": "2025-10-01T12:34:56.789Z"
  }
}
```

#### **Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| totalFeedback | integer | Total number of feedback entries |
| averageRating | float | Average rating (1.0 - 5.0) |
| sentiment.positive | integer | Count of positive feedback |
| sentiment.neutral | integer | Count of neutral feedback |
| sentiment.negative | integer | Count of negative feedback |
| sentimentPercentage | object | Percentage breakdown of sentiment |
| lastUpdated | string | ISO 8601 timestamp of last update |

#### **Example cURL**
```bash
curl -X GET https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/analytics \
  -H "X-API-Key: your-api-key"
```

#### **Example Python**
```python
import requests

def get_analytics():
    url = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/analytics'
    headers = {
        'X-API-Key': 'your-api-key'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"Total Feedback: {analytics['data']['totalFeedback']}")
        print(f"Average Rating: {analytics['data']['averageRating']}")
        print(f"Sentiment: {analytics['data']['sentiment']}")
    else:
        print(f"Error: {response.status_code}")

get_analytics()
```

---

### 4. Health Check

Check API availability and health status.

#### **Endpoint**
```http
GET /health
```

#### **Response**

**Success (200 OK):**
```json
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
```

#### **Example cURL**
```bash
curl -X GET https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/health
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "statusCode": 400,
  "error": "ValidationError",
  "message": "Invalid input parameters",
  "details": {
    "field": "email",
    "issue": "Invalid email format"
  }
}
```

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

#### **400 Bad Request**

**Validation Error:**
```json
{
  "statusCode": 400,
  "error": "ValidationError",
  "message": "Rating must be between 1 and 5",
  "details": {
    "field": "rating",
    "value": 6,
    "constraint": "min: 1, max: 5"
  }
}
```

**Missing Required Field:**
```json
{
  "statusCode": 400,
  "error": "ValidationError",
  "message": "Missing required field: email",
  "details": {
    "field": "email",
    "required": true
  }
}
```

#### **401 Unauthorized**
```json
{
  "statusCode": 401,
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

#### **429 Too Many Requests**
```json
{
  "statusCode": 429,
  "error": "RateLimitExceeded",
  "message": "Rate limit exceeded. Please try again later.",
  "details": {
    "limit": 1000,
    "window": "1 second",
    "retryAfter": 1
  }
}
```

#### **500 Internal Server Error**
```json
{
  "statusCode": 500,
  "error": "InternalServerError",
  "message": "An unexpected error occurred. Please contact support.",
  "requestId": "abc-123-def-456"
}
```

---

## Rate Limiting

### Limits

| Tier | Burst Limit | Steady-State Limit | Daily Quota |
|------|-------------|-------------------|-------------|
| Free | 100 req/sec | 500 req/sec | 10,000 requests |
| Basic | 500 req/sec | 2,000 req/sec | 100,000 requests |
| Premium | 1,000 req/sec | 5,000 req/sec | 1,000,000 requests |

### Rate Limit Headers

Responses include rate limit information in headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1633089600
```

### Handling Rate Limits

**Best Practices:**
1. Implement exponential backoff
2. Cache responses where appropriate
3. Monitor `X-RateLimit-Remaining` header
4. Handle 429 responses gracefully

**Example with Retry Logic:**
```javascript
const axios = require('axios');

async function makeRequestWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios(url, options);
      return response.data;
    } catch (error) {
      if (error.response?.status === 429) {
        const retryAfter = error.response.headers['retry-after'] || Math.pow(2, i);
        console.log(`Rate limited. Retrying after ${retryAfter}s...`);
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      } else {
        throw error;
      }
    }
  }
  throw new Error('Max retries exceeded');
}
```

---

## Examples

### Complete Integration Example (React)

```javascript
import axios from 'axios';

const API_BASE_URL = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod';
const API_KEY = 'your-api-key';

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  }
});

// Add response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 429) {
      console.error('Rate limit exceeded');
    } else if (error.response?.status === 500) {
      console.error('Server error');
    }
    return Promise.reject(error);
  }
);

// Create feedback
export const createFeedback = async (feedbackData) => {
  try {
    const response = await api.post('/feedback', feedbackData);
    return response.data;
  } catch (error) {
    console.error('Error creating feedback:', error);
    throw error;
  }
};

// List feedback with pagination
export const listFeedback = async (limit = 10, lastKey = null) => {
  try {
    const params = { limit };
    if (lastKey) params.lastKey = lastKey;
    
    const response = await api.get('/feedback', { params });
    return response.data;
  } catch (error) {
    console.error('Error listing feedback:', error);
    throw error;
  }
};

// Get analytics
export const getAnalytics = async () => {
  try {
    const response = await api.get('/analytics');
    return response.data;
  } catch (error) {
    console.error('Error fetching analytics:', error);
    throw error;
  }
};

// Health check
export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

// Usage in React component
const FeedbackForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    rating: 5,
    message: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const result = await createFeedback(formData);
      console.log('Feedback submitted:', result);
      alert('Thank you for your feedback!');
    } catch (error) {
      alert('Failed to submit feedback. Please try again.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};
```

---

### Python SDK Example

```python
import requests
from typing import Optional, Dict, Any

class FeedbackAPIClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        })
    
    def create_feedback(self, name: str, email: str, rating: int, message: str) -> Dict[Any, Any]:
        """Create new feedback entry"""
        payload = {
            'name': name,
            'email': email,
            'rating': rating,
            'message': message
        }
        response = self.session.post(f'{self.base_url}/feedback', json=payload)
        response.raise_for_status()
        return response.json()
    
    def list_feedback(self, limit: int = 10, last_key: Optional[str] = None) -> Dict[Any, Any]:
        """List feedback with pagination"""
        params = {'limit': limit}
        if last_key:
            params['lastKey'] = last_key
        
        response = self.session.get(f'{self.base_url}/feedback', params=params)
        response.raise_for_status()
        return response.json()
    
    def get_analytics(self) -> Dict[Any, Any]:
        """Get aggregated analytics"""
        response = self.session.get(f'{self.base_url}/analytics')
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[Any, Any]:
        """Check API health"""
        response = self.session.get(f'{self.base_url}/health')
        response.raise_for_status()
        return response.json()

# Usage
if __name__ == '__main__':
    client = FeedbackAPIClient(
        base_url='https://your-api-id.execute-api.us-east-1.amazonaws.com/prod',
        api_key='your-api-key'
    )
    
    # Create feedback
    result = client.create_feedback(
        name='John Doe',
        email='john@example.com',
        rating=5,
        message='Excellent service!'
    )
    print(f"Created feedback: {result['data']['feedbackId']}")
    
    # Get analytics
    analytics = client.get_analytics()
    print(f"Average rating: {analytics['data']['averageRating']}")
```

---

### Postman Collection

Import this collection into Postman for quick testing:

```json
{
  "info": {
    "name": "Serverless Feedback Platform API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create Feedback",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          },
          {
            "key": "X-API-Key",
            "value": "{{apiKey}}"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"John Doe\",\n  \"email\": \"john@example.com\",\n  \"rating\": 5,\n  \"message\": \"Great product!\"\n}"
        },
        "url": {
          "raw": "{{baseUrl}}/feedback",
          "host": ["{{baseUrl}}"],
          "path": ["feedback"]
        }
      }
    },
    {
      "name": "List Feedback",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "X-API-Key",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/feedback?limit=10",
          "host": ["{{baseUrl}}"],
          "path": ["feedback"],
          "query": [
            {
              "key": "limit",
              "value": "10"
            }
          ]
        }
      }
    },
    {
      "name": "Get Analytics",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "X-API-Key",
            "value": "{{apiKey}}"
          }
        ],
        "url": {
          "raw": "{{baseUrl}}/analytics",
          "host": ["{{baseUrl}}"],
          "path": ["analytics"]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
    },
    {
      "key": "apiKey",
      "value": "your-api-key"
    }
  ]
}
```

---

## Webhooks (Future)

### Event Types

| Event | Trigger | Payload |
|-------|---------|---------|
| feedback.created | New feedback submitted | Feedback object |
| feedback.updated | Feedback modified | Updated feedback object |
| analytics.updated | Analytics recalculated | Analytics summary |

### Webhook Configuration

```http
POST /webhooks
Content-Type: application/json

{
  "url": "https://your-domain.com/webhook",
  "events": ["feedback.created"],
  "secret": "your-webhook-secret"
}
```


---

<div align="center">
<sub>API Version 1.0 | Last Updated: October 2025</sub>
</div>