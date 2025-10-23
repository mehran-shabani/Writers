#!/usr/bin/env python3
"""MinIO bucket initialization script."""
import os
import sys
import boto3
import botocore.exceptions

endpoint = os.getenv("S3_ENDPOINT", "http://minio:9000")
access = os.getenv("S3_ACCESS_KEY", "minioadmin")
secret = os.getenv("S3_SECRET_KEY", "minioadmin")
bucket = os.getenv("S3_BUCKET", "writers")

s3 = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=access,
    aws_secret_access_key=secret
)

try:
    s3.head_bucket(Bucket=bucket)
    print(f"✓ Bucket '{bucket}' already exists.")
except botocore.exceptions.ClientError as e:
    error_code = e.response.get("Error", {}).get("Code", "")
    if error_code == "404":
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"✓ Bucket '{bucket}' created successfully.")
        except Exception as create_err:
            print(f"✗ Failed to create bucket: {create_err}")
            sys.exit(1)
    else:
        print(f"✗ Error checking bucket: {e}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)
