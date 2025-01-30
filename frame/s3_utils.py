from io import BytesIO

import boto3
from threading import Lock
from django.conf import settings

# 스레드 안전성을 위한 Lock 객체
lock = Lock()


def upload_file_to_s3(file, key, ExtraArgs=None):
    """
    AWS S3에 파일을 업로드하는 함수.

    :param file: 파일 객체 (open된 파일 또는 바이너리 데이터)
    :param key: S3 버킷 내 파일 경로 및 이름
    :param ExtraArgs: S3 업로드 옵션 (예: ContentType, ACL 등)
    :return: 업로드된 파일의 URL (성공 시), None (실패 시)
    """
    if isinstance(file, BytesIO):
        file.seek(0)

    with lock:
        s3_client = boto3.client(
            "s3",
            region_name=settings.STORAGES["default"]["OPTIONS"]["region_name"],
            aws_access_key_id=settings.STORAGES["default"]["OPTIONS"]["access_key"],
            aws_secret_access_key=settings.STORAGES["default"]["OPTIONS"]["secret_key"],
        )

        s3_bucket = settings.STORAGES["default"]["OPTIONS"]["bucket_name"]

        try:
            if isinstance(file, BytesIO):
                s3_client.upload_fileobj(file, s3_bucket, key, ExtraArgs)

            # S3 파일 URL 생성
            region = settings.STORAGES["default"]["OPTIONS"]["region_name"]
            url = f"https://{s3_bucket}.s3.{region}.amazonaws.com/{key}"
            return url

        except Exception as e:
            print(f"S3 업로드 오류: {e}")
            return None
