import json
import os
import time
import uuid
import boto3

# --- Secrets Manager helper ---
def get_secret(secret_name: str, region="ap-south-1"):
    client = boto3.client("secretsmanager", region_name=region)
    return json.loads(client.get_secret_value(SecretId=secret_name)["SecretString"])

# Pull AWS credentials
creds = get_secret("aws-lambda-creds")
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=creds["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=creds["AWS_SECRET_ACCESS_KEY"],
    region_name="ap-south-1"
)
TABLE = dynamodb.Table(os.environ.get("FEEDBACK_TABLE", "Feedbacks-prod"))

# Simple rule-based sentiment
POSITIVE = {'good','great','awesome','excellent','love','nice','fantastic','best','happy','satisfied'}
NEGATIVE = {'bad','terrible','awful','hate','worst','disappointed','poor','sad','angry','unsatisfied'}

def simple_sentiment(text: str) -> str:
    if not text: return "neutral"
    text_l = text.lower()
    pos = sum(1 for w in POSITIVE if w in text_l)
    neg = sum(1 for w in NEGATIVE if w in text_l)
    return "positive" if pos > neg else "negative" if neg > pos else "neutral"

def lambda_handler(event, context):
    try:
        data = json.loads(event.get("body") or "{}")
        name, email, message = data.get("name","").strip(), data.get("email","").strip(), data.get("message","").strip()
        rating = int(data.get("rating") or 0)

        if not message:
            return {"statusCode":400, "headers":cors_headers(), "body": json.dumps({"error":"message required"})}

        item = {
            "feedback_id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "message": message,
            "rating": rating,
            "sentiment": simple_sentiment(message),
            "created_at": int(time.time())
        }

        TABLE.put_item(Item=item)

        return {"statusCode":201, "headers":cors_headers(), "body": json.dumps({"ok": True, "feedback_id": item["feedback_id"]})}

    except Exception as e:
        print("create_feedback error:", e)
        raise

def cors_headers():
    return {"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"Content-Type","Access-Control-Allow-Methods":"OPTIONS,POST,GET"}
