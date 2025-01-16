from datetime import datetime

from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response


from photo.models import Photo
from photo.serializer import CreatePhotoSerializer
from user.models import User


class CreatePhotoView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="최종 사진본 생성 API",
        operation_description="최종 사진본 생성",
        manual_parameters=[
            openapi.Parameter(
                name="userId",
                in_=openapi.IN_FORM,
                description="유저 아이디",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="photoImg",
                in_=openapi.IN_FORM,
                description="업로드할 사진 파일",
                type=openapi.TYPE_FILE,
                required=True,
            )
        ],
        responses={
            201: openapi.Response(
                description="최종 사진 생성 성공",
                examples={
                    "application/json": {
                        "code": "PHO_2011",
                        "message": "최종 사진 생성에 성공했습니다.",
                        "photoId": 1,
                        "photoUrl": "https://example-bucket.s3.amazonaws.com/example.jpg"
                    }
                }
            ),
            400: openapi.Response(
                description="최종 사진 생성 실패",
                examples={
                    "application/json": {
                        "code": "PHO_4001",
                        "message": "최종 사진 생성에 실패했습니다."
                    }
                }
            ),
        },
    )

    def post(self, request):
        serializer = CreatePhotoSerializer(data=request.data)
        user_id = request.data.get("userId")

        user = get_object_or_404(User, id=int(user_id))

        if not serializer.is_valid():
            return Response({
                "code": "PHO_4001",
                "status": 400,
                "message": "유효하지 않은 데이터입니다.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('photoImg')
        if not file:
            return Response({
                "code": "PHO_4001",
                "status": 400,
                "message": "이미지를 업로드해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        file_name = f"photos/{timestamp}_{file.name}"

        try:
            s3_url = self.upload_to_s3(file, file_name)
        except Exception as e:
            return Response({
                "code": "PHO_4001",
                "status": 400,
                "message": f"S3 업로드 실패: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        photo = Photo.objects.create(
            userId=user,
            photoUrl=s3_url
        )

        return Response({
            "code": "PHO_2011",
            "status": 201,
            "message": "최종 사진 생성에 성공했습니다.",
            "photoId": photo.photoId,
            "photoUrl": photo.photoUrl
        }, status=status.HTTP_201_CREATED)

    def upload_to_s3(self, image, file_name):
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        file_path = default_storage.save(file_name, ContentFile(image.read()))
        return default_storage.url(file_path)