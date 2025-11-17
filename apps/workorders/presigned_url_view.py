# location: apps/workorders/presigned_url_view.py
from rest_framework.decorators import api_view, permission_classes
import boto3, os, uuid
from datetime import timedelta

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def presigned_url_view(request):
    ot_id = request.data.get("ot")
    filename = request.data.get("filename")
    content_type = request.data.get("content_type") or "application/octet-stream"

    bucket = os.getenv("AWS_STORAGE_BUCKET_NAME", "pgf-evidencias")
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL", "http://localstack:4566"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
        region_name=os.getenv("AWS_S3_REGION_NAME", "us-east-1"),
    )

    key = f"evidencias/ot_{ot_id}/{uuid.uuid4()}_{filename}"

    post = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}],
        ExpiresIn=600,
    )

    file_url = f"{os.getenv('AWS_PUBLIC_URL_PREFIX','http://localstack:4566')}/{bucket}/{key}"
    return Response({"upload": post, "file_url": file_url})