from datetime import datetime

from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
import logging
logger = logging.getLogger("inframe")

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
            ),
            openapi.Parameter(
                name="location",
                in_=openapi.IN_FORM,
                description="사진이 촬영된 장소",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            201: openapi.Response(
                description="최종 사진 생성 성공",
                examples={
                    "application/json": {
                        "code": "PHO_2011",
                        "message": "최종 사진 생성에 성공했습니다.",
                        "photoId": 1,
                        "photoUrl": "https://example-bucket.s3.amazonaws.com/example.jpg",
                        "location": "서울특별시 강남구"
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
        location = request.data.get("location", None)
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
            photo_url=s3_url,
            location=location
        )

        return Response({
            "code": "PHO_2011",
            "status": 201,
            "message": "최종 사진 생성에 성공했습니다.",
            "photo_id": photo.photo_id,
            "photo_url": photo.photo_url,
            "location": photo.location

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

        # 사용자 조회
        user = get_object_or_404(User, user_id=user_id)

        # 삭제되지 않은 사진만 필터링하고 날짜별로 그룹화
        photos = Photo.objects.filter(user=user, is_deleted=False).annotate(
            date=TruncDate('created_at')  # 날짜별로 그룹화
        ).order_by('-date')  # 최근 날짜 순으로 정렬

        grouped_photos = {}

        # 날짜별로 사진 그룹화
        for photo in photos:
            date = photo.date.strftime('%Y.%m.%d')  # 날짜 포맷
            if date not in grouped_photos:
                grouped_photos[date] = []

            # 시리얼라이저를 통해 사진 데이터 추가
            serialized_photo = PhotoListSerializer(photo).data
            grouped_photos[date].append(serialized_photo)

        # 날짜별로 그룹화된 데이터를 리스트로 변환
        data = [
            {
                "date": date,
                "photos": photos
            } for date, photos in grouped_photos.items()
        ]

        # 성공적으로 응답 반환
        return Response({
            "code": "PHO_2001",
            "status": 200,
            "message": "사진 목록 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)

class PhotoSingleView(APIView):
    @swagger_auto_schema(
        operation_summary="최종 사진 조회 API",
        operation_description="최종 사진 조회",
        responses={
            200: openapi.Response(
                description="최종 사진 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="응답 코드"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="응답 메시지"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "photo_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="최종 사진 ID"),
                                "photo_url": openapi.Schema(type=openapi.TYPE_STRING, description="최종 사진 URL"),
                                "location": openapi.Schema(type=openapi.TYPE_STRING, description="사진이 촬영된 장소"),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time", description="사진이 촬영된 날짜 및 시간"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="최종 사진 조회 실패",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="에러 코드"),
                        "status": openapi.Schema(type=openapi.TYPE_INTEGER, description="HTTP 상태 코드"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="에러 메시지"),
                    },
                ),
            ),
        },
    )
    def get(self, request, photo_id):
        try:
            photo = Photo.objects.get(pk=photo_id)
            logger.info(f"photo: {photo}")
            response_data = {
                "code": "PHO_2001",
                "status": 200,
                "message": "최종 사진 조회 성공",
                "data": {
                    "photo_id" : photo.photo_id,
                    "photo_url": photo.photo_url,
                    "location": photo.location,
                    "created_at": photo.created_at.strftime('%Y-%m-%d %H:%M:%S') if photo.created_at else "날짜 정보 없음"
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error creating photo: {str(e)}")
            response_data = {
                "code": "PHO_5002",
                "status": 500,
                "message": f"최종 사진 조회 실패: {str(e)}",
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)