from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class CloudFrontS3Storage(S3Boto3Storage):
    def __init__(self, *args, **kwargs):
        self.custom_domain = settings.CLOUDFRONT_URL
        super().__init__(*args, **kwargs)