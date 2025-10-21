import os
import json
import boto3
from botocore.exceptions import ClientError

# --- Fetch AWS credentials from Secrets Manager ---
def get_secret(secret_name: str, region_name: str = "ap-south-1"):
    client = boto3.client('secretsmanager', region_name=region_name)
    try:
        return json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])
    except ClientError as e:
        print(f"Error retrieving secret {secret_name}: {e}")
        raise

# Pull AWS credentials
creds = get_secret("aws-lambda-creds")
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=creds["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=creds["AWS_SECRET_ACCESS_KEY"],
    region_name="ap-south-1"
)

TABLE = dynamodb.Table(os.environ.get('ANALYTICS_TABLE', 'Analytics-prod'))

def lambda_handler(event, context):
    try:
        for rec in event.get('Records', []):
            if rec.get('eventName') != 'INSERT':
                continue
            new = rec['dynamodb'].get('NewImage', {})
            rating = int(new.get('rating', {}).get('N', 0))
            sentiment = new.get('sentiment', {}).get('S', 'neutral')

            # Update metrics
            TABLE.update_item(Key={'metric_id': 'total_feedbacks'}, UpdateExpression='ADD #v :inc',
                              ExpressionAttributeNames={'#v': 'value'}, ExpressionAttributeValues={':inc': 1})
            TABLE.update_item(Key={'metric_id': 'sum_ratings'}, UpdateExpression='ADD #v :inc',
                              ExpressionAttributeNames={'#v': 'value'}, ExpressionAttributeValues={':inc': rating})

            # Update sentiment counters in one block
            TABLE.update_item(
                Key={'metric_id': f'{sentiment}_count'},
                UpdateExpression='ADD #v :inc',
                ExpressionAttributeNames={'#v': 'value'},
                ExpressionAttributeValues={':inc': 1}
            )

        return {'statusCode': 200}

    except Exception as e:
        print('analytics_updater error:', e)
        raise
