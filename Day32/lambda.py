import boto3
import uuid
from datetime import datetime, timezone
from botocore.exceptions import ClientError

# -----------------------------
# Configuration
# -----------------------------
REGION = "af-south-1"
DYNAMODB_TABLE_NAME = "inventory"

# -----------------------------
# AWS Clients
# -----------------------------
ec2 = boto3.client("ec2", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def lambda_handler(event, context):
    """
    Lambda entry point.
    Scans all EBS volumes in the region and stores UNENCRYPTED volumes in DynamoDB.
    """
    discovered = 0
    errors = 0

    try:
        paginator = ec2.get_paginator("describe_volumes")

        for page in paginator.paginate():
            for volume in page.get("Volumes", []):
                # Only process unencrypted volumes
                if volume.get("Encrypted") is False:
                    try:
                        store_volume(volume)
                        discovered += 1
                    except Exception as e:
                        print(
                            f"Error storing volume {volume.get('VolumeId')}: {e}"
                        )
                        errors += 1

    except ClientError as e:
        # Fail hard if AWS API itself fails
        print(f"AWS API error: {e}")
        raise

    return {
        "status": "completed",
        "unencrypted_volumes_recorded": discovered,
        "errors": errors,
        "region": REGION,
        "timestamp": current_timestamp()
    }


def store_volume(volume):
    """
    Stores a single unencrypted EBS volume discovery.
    Uses itemId (UUID) as the DynamoDB partition key to preserve full history.
    """
    item = {
        # REQUIRED partition key
        "itemId": str(uuid.uuid4()),

        # Business attributes
        "VolumeId": volume["VolumeId"],
        "Encrypted": volume["Encrypted"],
        "Region": REGION,
        "AvailabilityZone": volume["AvailabilityZone"],
        "SizeGiB": volume["Size"],
        "VolumeType": volume["VolumeType"],
        "State": volume["State"],
        "DiscoveryTimestamp": current_timestamp()
    }

    table.put_item(Item=item)


def current_timestamp():
    """
    Returns current UTC timestamp in ISO 8601 format.
    """
    return datetime.now(timezone.utc).isoformat()
