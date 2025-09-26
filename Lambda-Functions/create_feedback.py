import json
import os
import time
import uuid
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
FEEDBACK_TABLE = os.environ.get('FEEDBACK_TABLE', 'Feedbacks-prod')
TABLE = dynamodb.Table(FEEDBACK_TABLE)

# Simple rule-based sentiment (small & fast)
POSITIVE = {
    'good', 'great', 'awesome', 'excellent', 'love', 'nice',
    'fantastic', 'best', 'happy', 'satisfied'
}
NEGATIVE = {
    'bad', 'terrible', 'awful', 'hate', 'worst', 'disappointed',
    'poor', 'sad', 'angry', 'unsatisfied'
}


def simple_sentiment(text: str) -> str:
    if not text:
        return 'neutral'

    text_l = text.lower()
    pos = sum(1 for w in POSITIVE if w in text_l)
    neg = sum(1 for w in NEGATIVE if w in text_l)

    if pos > neg:
        return 'positive'
    if neg > pos:
        return 'negative'
    return 'neutral'


def lambda_handler(event, context):
    # API Gateway REST proxy: event['body'] contains JSON string
    try:
        body = event.get('body')
        if isinstance(body, str):
            data = json.loads(body)
        else:
            data = body or {}

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()
        rating = (
            int(data.get('rating', 0))
            if data.get('rating') is not None else 0
        )

        if not message:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'message required'})
            }

        sentiment = simple_sentiment(message)

        item = {
            'feedback_id': str(uuid.uuid4()),
            'name': name,
            'email': email,
            'message': message,
            'rating': rating,
            'sentiment': sentiment,
            'created_at': int(time.time())
        }

        TABLE.put_item(Item=item)

        return {
            'statusCode': 201,
            'headers': cors_headers(),
            'body': json.dumps({'ok': True, 'feedback_id': item['feedback_id']})
        }

    except Exception as e:
        print('Exception in create_feedback:', str(e))
        # Let stacktraces appear in CloudWatch logs -> metric filters will detect
        raise


def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    }
