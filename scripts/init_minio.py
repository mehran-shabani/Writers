import os, boto3, botocore

endpoint = os.getenv("S3_ENDPOINT","http://minio:9000")
access = os.getenv("S3_ACCESS_KEY","minioadmin")
secret = os.getenv("S3_SECRET_KEY","minioadmin")
bucket = os.getenv("S3_BUCKET","writers")

s3 = boto3.client("s3", endpoint_url=endpoint, aws_access_key_id=access, aws_secret_access_key=secret)
try:
    s3.head_bucket(Bucket=bucket)
    print("Bucket exists.")
except botocore.exceptions.ClientError:
    s3.create_bucket(Bucket=bucket)
    print("Bucket created.")
