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
TABLE = dynamodb.Table(os.environ.get("FEEDBACK_TABLE", "Feedbacks-prod"))

def lambda_handler(event, context):
    try:
        limit = int((event.get('queryStringParameters') or {}).get('limit', 50))
        items = TABLE.scan(Limit=limit).get('Items', [])
        items.sort(key=lambda x: x.get('created_at',0), reverse=True)

        return {"statusCode":200, "headers":cors_headers(), "body":json.dumps({"items": items})}

    except Exception as e:
        print("list_feedbacks error:", e)
        raise

def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,GET"
    }
