import os
import boto3
import json

# Initialize Lambda client
lambda_client = boto3.client('lambda')

TARGET = os.environ.get('TARGET_FUNCTION_NAME', 'fb-create-prod')
ALIAS = os.environ.get('ALIAS_NAME', 'prod')

def lambda_handler(event, context):
    print('Rollback invoked. Event:', json.dumps(event))
    
    try:
        alias = lambda_client.get_alias(FunctionName=TARGET, Name=ALIAS)
        current_version = alias.get('FunctionVersion')
        print('Current alias version:', current_version)

        # List all published versions (excluding $LATEST)
        versions = lambda_client.list_versions_by_function(FunctionName=TARGET)
        vers = [v['Version'] for v in versions.get('Versions', []) if v['Version'] != '$LATEST']
        vers_sorted = sorted([int(v) for v in vers])
        print('Published versions:', vers_sorted)

        # Find previous version < current_version
        prev = None
        for v in reversed(vers_sorted):
            if v < int(current_version):
                prev = str(v)
                break

        if not prev:
            print('No previous version found. No rollback performed.')
            return {'statusCode': 200, 'message': 'no-prev'}

        # Update alias to point to previous version
        resp = lambda_client.update_alias(
            FunctionName=TARGET,
            Name=ALIAS,
            FunctionVersion=prev
        )
        print('Alias updated to version', prev)
        return {'statusCode': 200, 'message': 'rolled-back', 'to': prev}

    except Exception as e:
        print('Rollback error:', str(e))
        raise
