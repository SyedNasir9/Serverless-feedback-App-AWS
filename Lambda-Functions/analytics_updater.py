import os
import json
import boto3

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
ANALYTICS_TABLE = os.environ.get('ANALYTICS_TABLE', 'Analytics-prod')
TABLE = dynamodb.Table(ANALYTICS_TABLE)


def lambda_handler(event, context):
    try:
        for rec in event.get('Records', []):
            if rec.get('eventName') != 'INSERT':
                continue

            new = rec['dynamodb'].get('NewImage', {})

            # DynamoDB JSON to native
            feedback_id = new.get('feedback_id', {}).get('S')
            rating = int(new.get('rating', {}).get('N', 0)) if 'rating' in new else 0
            sentiment = new.get('sentiment', {}).get('S', 'neutral')

            # --- Update counters using atomic UpdateItem ---

            # total_feedbacks += 1
            TABLE.update_item(
                Key={'metric_id': 'total_feedbacks'},
                UpdateExpression='ADD #v :inc',
                ExpressionAttributeNames={'#v': 'value'},
                ExpressionAttributeValues={':inc': 1}
            )

            # sum_ratings += rating
            TABLE.update_item(
                Key={'metric_id': 'sum_ratings'},
                UpdateExpression='ADD #v :inc',
                ExpressionAttributeNames={'#v': 'value'},
                ExpressionAttributeValues={':inc': rating}
            )

            # sentiment counters
            if sentiment == 'positive':
                TABLE.update_item(
                    Key={'metric_id': 'positive_count'},
                    UpdateExpression='ADD #v :inc',
                    ExpressionAttributeNames={'#v': 'value'},
                    ExpressionAttributeValues={':inc': 1}
                )
            elif sentiment == 'negative':
                TABLE.update_item(
                    Key={'metric_id': 'negative_count'},
                    UpdateExpression='ADD #v :inc',
                    ExpressionAttributeNames={'#v': 'value'},
                    ExpressionAttributeValues={':inc': 1}
                )
            else:
                TABLE.update_item(
                    Key={'metric_id': 'neutral_count'},
                    UpdateExpression='ADD #v :inc',
                    ExpressionAttributeNames={'#v': 'value'},
                    ExpressionAttributeValues={':inc': 1}
                )

        return {'statusCode': 200}

    except Exception as e:
        print('analytics_updater error:', e)
        raise
