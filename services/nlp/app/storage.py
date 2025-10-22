import os, boto3, botocore, datetime as dt
from urllib.parse import urljoin

ENDPOINT = os.getenv("S3_ENDPOINT","http://minio:9000")
ACCESS = os.getenv("S3_ACCESS_KEY","minioadmin")
SECRET = os.getenv("S3_SECRET_KEY","minioadmin")
BUCKET = os.getenv("S3_BUCKET","writers")

s3 = boto3.client("s3", endpoint_url=ENDPOINT, aws_access_key_id=ACCESS, aws_secret_access_key=SECRET)

def upload_bytes(key: str, data: bytes, content_type="application/octet-stream"):
    s3.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)
    return key

def presign(key: str, expires=3600):
    return s3.generate_presigned_url("get_object", Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=expires)

def download_to_bytes(key: str) -> bytes:
    obj = s3.get_object(Bucket=BUCKET, Key=key)
    return obj["Body"].read()
