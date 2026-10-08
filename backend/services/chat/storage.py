import os
import tempfile
import time
from uuid import UUID
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from config import (S3_ACCESS_KEY, S3_BUCKET, S3_ENDPOINT_URL, S3_REGION, S3_SECRET_KEY)

_client = boto3.client(
    "s3",
    region_name=S3_REGION,
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(s3={"addressing_style": "path"}),
)


def ensure_bucket(retries: int = 30) -> None:
    if not S3_ENDPOINT_URL:
        return
    for _ in range(retries):
        try:
            _client.head_bucket(Bucket=S3_BUCKET)
            return
        except ClientError as e:
            if e.response["Error"]["Code"] in ("404", "NoSuchBucket", "NotFound"):
                _client.create_bucket(Bucket=S3_BUCKET)
                return
            raise
        except EndpointConnectionError:
            time.sleep(2)
    raise RuntimeError("S3 endpoint never became reachable")


def object_key(document_id: UUID) -> str:
    return f"documents/{document_id}.pdf"


async def upload_file(file: UploadFile, document_id: UUID, max_size: int) -> None:
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)
    if size > max_size:
        raise ValueError(f"File exceeds the {max_size // (1024 * 1024)} MB limit")

    await run_in_threadpool(
        _client.upload_fileobj,
        file.file,
        S3_BUCKET,
        object_key(document_id),
        ExtraArgs={"ContentType": "application/pdf"},
    )


def download_to_temp(document_id: UUID) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        _client.download_fileobj(S3_BUCKET, object_key(document_id), tmp)
    except Exception:
        tmp.close()
        os.remove(tmp.name)
        raise
    tmp.close()
    return tmp.name


def delete_file(document_id: UUID) -> None:
    _client.delete_object(Bucket=S3_BUCKET, Key=object_key(document_id))