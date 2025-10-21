import os
import boto3
import json

# --- Secrets Manager helper ---
def get_secret(secret_name: str, region="ap-south-1"):
    client = boto3.client("secretsmanager", region_name=region)
    return json.loads(client.get_secret_value(SecretId=secret_name)["SecretString"])

# Fetch AWS creds
creds = get_secret("aws-lambda-creds")
lambda_client = boto3.client(
    "lambda",
    aws_access_key_id=creds["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=creds["AWS_SECRET_ACCESS_KEY"],
    region_name="ap-south-1"
)

TARGET = os.environ.get("TARGET_FUNCTION_NAME", "fb-create-prod")
ALIAS = os.environ.get("ALIAS_NAME", "prod")

def lambda_handler(event, context):
    print("Rollback invoked. Event:", json.dumps(event))
    try:
        current = lambda_client.get_alias(FunctionName=TARGET, Name=ALIAS)["FunctionVersion"]
        versions = [
            int(v["Version"]) for v in lambda_client.list_versions_by_function(FunctionName=TARGET).get("Versions", [])
            if v["Version"] != "$LATEST"
        ]
        prev = str(max([v for v in versions if v < int(current)], default=None))
        if not prev:
            print("No previous version found. Skipping rollback.")
            return {"statusCode": 200, "message": "no-prev"}

        lambda_client.update_alias(FunctionName=TARGET, Name=ALIAS, FunctionVersion=prev)
        print("Alias updated to version", prev)
        return {"statusCode": 200, "message": "rolled-back", "to": prev}

    except Exception as e:
        print("Rollback error:", e)
        raise
