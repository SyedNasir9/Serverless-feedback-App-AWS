import json
import os
import boto3

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
ANALYTICS_TABLE = os.environ.get('ANALYTICS_TABLE', 'Analytics-prod')
TABLE = dynamodb.Table(ANALYTICS_TABLE)

def lambda_handler(event, context):
    try:
        # Scan the DynamoDB table
        res = TABLE.scan()
        items = {item['metric_id']: item.get('value', 0) for item in res.get('Items', [])}

        # Compute average rating if sum_ratings & total_feedbacks exist
        total = items.get('total_feedbacks', 0)
        sum_r = items.get('sum_ratings', 0)
        avg = (sum_r / total) if total and sum_r else 0
        items['avg_rating'] = avg

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps(items)
        }

    except Exception as e:
        print('list_analytics error:', e)
        raise

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,GET'
    }
