from datetime import datetime

from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response


from photo.models import Photo
from photo.serializer import CreatePhotoSerializer, PhotoListSerializer
from user.models import User


class CreatePhotoView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="최종 사진본 생성 API",
        operation_description="최종 사진본 생성",
        manual_parameters=[
            openapi.Parameter(
                name="user_id",
                in_=openapi.IN_FORM,
                description="유저 아이디",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="photo_img",
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
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        serializer = CreatePhotoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "code": "PHO_4001",
                "status": 400,
                "message": "유효하지 않은 데이터입니다.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES.get('photo_img')
        if not file:
            return Response({
                "code": "PHO_4001",
                "status": 400,
                "message": "이미지를 업로드해주세요."
            }, status=status.HTTP_400_BAD_REQUEST)

        file_name = f"photos/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"

        try:
            s3_url = self.upload_to_s3(file, file_name)
        except Exception as e:
            return Response({
                "code": "PHO_4001",
                "status": 400,
                "message": f"S3 업로드 실패: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        photo = Photo.objects.create(
            user_id=user.user_id,
            photo_url=s3_url
        )

        return Response({
            "code": "PHO_2011",
            "status": 201,
            "message": "최종 사진 생성에 성공했습니다.",
            "photo_id": photo.photo_id,
            "photo_url": photo.photo_url
        }, status=status.HTTP_201_CREATED)

    def upload_to_s3(self, image, file_name):
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        file_path = default_storage.save(file_name, ContentFile(image.read()))
        return default_storage.url(file_path)

class PhotoListView(APIView):
    @swagger_auto_schema(
        operation_summary="갤러리 목록 조회 API",
        operation_description="사용자가 저장한 사진 목록을 날짜별로 조회",
        manual_parameters=[
            openapi.Parameter(
                name="user_id",
                in_=openapi.IN_QUERY,
                description="조회할 유저의 ID",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="저장된 사진 목록 조회 성공",
                examples={
                    "application/json": {
                        "code": "PHO_2001",
                        "message": "나의 저장된 사진 목록 조회 성공",
                        "data": [
                            {
                                "date": "2025-01-13",
                                "photos": [
                                    {
                                        "photo_id": 1,
                                        "photo_url": "https://example.com/photo1.jpg"
                                    },
                                    {
                                        "photo_id": 2,
                                        "photo_url": "https://example.com/photo2.jpg"
                                    }
                                ]
                            },
                            {
                                "date": "2025-01-14",
                                "photos": [
                                    {
                                        "photo_id": 3,
                                        "photo_url": "https://example.com/photo3.jpg"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "code": "PHO_4001",
                        "message": "요청이 잘못되었습니다."
                    }
                }
            ),
        },
    )
    def get(self, request):
        user_id = request.query_params.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        photos = Photo.objects.filter(user=user, is_deleted=False).annotate(
            date=TruncDate('created_at')
        ).order_by('date')

        grouped_photos = {}
        for photo in photos:
            date = photo.date.strftime('%Y.%m.%d')
            if date not in grouped_photos:
                grouped_photos[date] = []

            serialized_photo = PhotoListSerializer(photo).data
            grouped_photos[date].append(serialized_photo)

        data = [
            {
                "date": date,
                "photos": photos
            } for date, photos in grouped_photos.items()
        ]

        return Response({
            "code": "PHO_2001",
            "message": "사진 목록 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)