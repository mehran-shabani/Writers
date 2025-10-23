import os
import boto3
import botocore.exceptions

ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
ACCESS = os.getenv("S3_ACCESS_KEY", "minioadmin")
SECRET = os.getenv("S3_SECRET_KEY", "minioadmin")
BUCKET = os.getenv("S3_BUCKET", "writers")

s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT,
    aws_access_key_id=ACCESS,
    aws_secret_access_key=SECRET
)


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    """Upload bytes to S3/MinIO storage."""
    try:
        s3.put_object(Bucket=BUCKET, Key=key, Body=data, ContentType=content_type)
        return key
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"Failed to upload {key} to S3: {e}") from e


def presign(key: str, expires: int = 3600) -> str:
    """Generate presigned URL for downloading object."""
    try:
        return s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=expires
        )
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"Failed to presign {key}: {e}") from e


def download_to_bytes(key: str) -> bytes:
    """Download object from S3/MinIO as bytes."""
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
        return obj["Body"].read()
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"Failed to download {key} from S3: {e}") from e
