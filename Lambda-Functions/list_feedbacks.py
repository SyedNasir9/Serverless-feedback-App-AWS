import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
FEEDBACK_TABLE = os.environ.get('FEEDBACK_TABLE', 'Feedbacks-prod')
TABLE = dynamodb.Table(FEEDBACK_TABLE)


def lambda_handler(event, context):
    try:
        # optional query param ?limit=20
        params = event.get('queryStringParameters') or {}
        limit = int(params.get('limit', '50'))

        res = TABLE.scan(Limit=limit)
        items = res.get('Items', [])

        # sort by created_at desc
        items.sort(key=lambda x: x.get('created_at', 0), reverse=True)

        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'items': items})
        }

    except Exception as e:
        print('Exception in list_feedbacks:', str(e))
        raise


def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,GET'
    }
