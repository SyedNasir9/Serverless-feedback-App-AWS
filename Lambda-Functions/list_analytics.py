import json
import os
import boto3

# --- Secrets Manager helper ---
def get_secret(secret_name: str, region="ap-south-1"):
    client = boto3.client("secretsmanager", region_name=region)
    return json.loads(client.get_secret_value(SecretId=secret_name)["SecretString"])

# Pull AWS creds
creds = get_secret("aws-lambda-creds")
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=creds["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=creds["AWS_SECRET_ACCESS_KEY"],
    region_name="ap-south-1"
)
TABLE = dynamodb.Table(os.environ.get("ANALYTICS_TABLE", "Analytics-prod"))

def lambda_handler(event, context):
    try:
        items = {item['metric_id']: item.get('value',0) for item in TABLE.scan().get('Items', [])}
        total, sum_r = items.get('total_feedbacks',0), items.get('sum_ratings',0)
        items['avg_rating'] = (sum_r / total) if total else 0

        return {"statusCode":200, "headers":cors_headers(), "body":json.dumps(items)}

    except Exception as e:
        print("list_analytics error:", e)
        raise

def cors_headers():
    return {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"Content-Type","Access-Control-Allow-Methods":"OPTIONS,GET"}
