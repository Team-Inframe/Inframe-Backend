from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomFrame, Sticker, CustomFrameSticker
from user.models import User
from frame.models import Frame
from .s3_utils import upload_file_to_s3
from io import BytesIO
from PIL import Image
import time
import logging
import json
from rest_framework.parsers import MultiPartParser

logger = logging.getLogger("inframe")


class CustomFrameCreateView(APIView):
    
    # MultiPartParser를 통해 파일 업로드를 처리
    parser_classes = [MultiPartParser]
    
    @swagger_auto_schema(
        operation_summary="커스텀 프레임 생성 API",
        operation_description="form-data로 커스텀 프레임을 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'custom_frame_img',
                openapi.IN_FORM,
                description='커스텀 프레임 이미지 파일',
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'data',
                openapi.IN_FORM,
                description='커스텀 프레임 데이터(JSON 문자열)',
                type=openapi.TYPE_STRING,
                required=True
            ),            
        ],
        responses={
            200: openapi.Response(
                description="성공적으로 커스텀 프레임 생성",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="응답 코드"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="응답 메시지"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "custom_frame_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="커스텀 프레임 ID"),
                            },
                        ),
                    },
                ),
            ),
            500: openapi.Response(
                description="서버 오류",
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
    def post(self, request):
        try:
            data_str = request.POST.get("data", None)
            data = json.loads(data_str)
            logger.info(f"data : {data}")
            logger.info(f"user_id : {data.get('user_id')}")
            custom_frame_img = request.FILES.get("custom_frame_img")
            # 이미지 저장 처리
            image_data = custom_frame_img.read()
            img = Image.open(BytesIO(image_data))
            custom_frame_img_name = f"custom_frame_{int(time.time())}.jpg"
            img_file = BytesIO()
            img.save(img_file, format="JPEG")
            img_file.seek(0)

            custom_frame_img_url = upload_file_to_s3(
                file=img_file,
                key=custom_frame_img_name,
                ExtraArgs={
                    "ContentType": "image/jpeg",
                    "ACL": "public-read",
                },
            )

            user = User.objects.get(user_id=data.get("user_id"))
            frame = Frame.objects.get(frame_id=data.get("frame_id"))

            custom_frame = CustomFrame.objects.create(
                user=user,
                frame=frame,
                custom_frame_title=data.get("custom_frame_title"),
                custom_frame_url=custom_frame_img_url,
                is_shared=data.get("is_shared", False),
                is_bookmarked=False,
                is_deleted=False,
            )

            # Sticker 데이터 저장 및 관계 추가
            stickers = data.get("stickers", [])
            
            for sticker_data in stickers:
                # sticker_id 추출 및 로그
                sticker_id = sticker_data.get("sticker_id")
                
                sticker = Sticker.objects.get(sticker_id=sticker_id)
                                
                # CustomFrameSticker 저장
                CustomFrameSticker.objects.create(
                    custom_frame=custom_frame,
                    sticker=sticker,
                    position_x=sticker_data.get("position_x"),
                    position_y=sticker_data.get("position_y"),
                    sticker_width=sticker_data.get("sticker_width"),
                    sticker_height=sticker_data.get("sticker_height"),
                    is_deleted=False,
                )

            # 성공 응답
            return Response(
                {
                    "code": "CSF_2001",
                    "status": 201,
                    "message": "커스텀 프레임 생성 성공",
                    "data": {"custom_frame_id": custom_frame.custom_frame_id},
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "code": "CSF_5001",
                    "status": 500,
                    "message": "서버 오류: {}".format(str(e)),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomFrameListView(APIView):
    @swagger_auto_schema(
        operation_summary="커스텀 프레임 목록 조회",
        operation_description="커스텀 프레임의 목록을 조회합니다. 정렬 방식은 최신순(default) 또는 북마크수순으로 가능합니다.",
        manual_parameters=[
            openapi.Parameter(
                "sort",
                openapi.IN_QUERY,
                description="정렬 방식 (latest: 최신순, bookmarks: 북마크수순)",
                type=openapi.TYPE_STRING,
                required=False,
                enum=["latest", "bookmarks"],
            ),
        ],
        responses={
            200: openapi.Response(
                description="커스텀 프레임 목록 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="응답 코드"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="응답 메시지"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "customFrames": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "customFrameId": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="커스텀 프레임 ID",
                                            ),
                                            "customFrameTitle": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="커스텀 프레임 제목",
                                            ),
                                            "customFrameUrl": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                description="커스텀 프레임 URL",
                                            ),
                                            "bookmarks": openapi.Schema(
                                                type=openapi.TYPE_INTEGER,
                                                description="북마크 수",
                                            ),
                                            "created_at": openapi.Schema(
                                                type=openapi.TYPE_STRING,
                                                format="date-time",
                                                description="생성 시간",
                                            ),
                                        },
                                    ),
                                ),
                            },
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="커스텀 프레임 목록 조회 실패",
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
    def get(self, request):
        try:
            sort_option = request.GET.get("sort", "latest")
            if sort_option == "bookmarks":
                custom_frames = CustomFrame.objects.filter(is_deleted=False).order_by("-bookmarks")
            else:  # 기본값: 최신순 정렬
                custom_frames = CustomFrame.objects.filter(is_deleted=False).order_by("-created_at")

            if not custom_frames.exists():
                return Response(
                    {
                        "code": "CSF_4041",
                        "status": 404,
                        "message": "커스텀 프레임 목록 조회 실패",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            custom_frames_data = [
                {
                    "customFrameId": frame.custom_frame_id,
                    "customFrameTitle": frame.custom_frame_title,
                    "customFrameUrl": frame.custom_frame_url,
                    "bookmarks": frame.bookmarks,
                    "created_at": frame.created_at.isoformat(),
                }
                for frame in custom_frames
            ]

            return Response(
                {
                    "code": "CSF_2001",
                    "status": 200,
                    "message": "커스텀 프레임 목록 조회 성공",
                    "data": {"customFrames": custom_frames_data},
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "code": "CSF_5001",
                    "status": 500,
                    "message": f"서버 오류: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )