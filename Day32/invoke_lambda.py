import boto3
import json

LAMBDA_FUNCTION_NAME = "storage_function"
REGION = "af-south-1"

lambda_client = boto3.client("lambda", region_name=REGION)

def invoke_lambda():
    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType="RequestResponse",  # Waits for execution to finish
        Payload=json.dumps({})
    )

    payload = response["Payload"].read().decode("utf-8")

    print("Lambda Status Code:", response["StatusCode"])
    print("Lambda Response:")
    print(payload)


if __name__ == "__main__":
    invoke_lambda()
