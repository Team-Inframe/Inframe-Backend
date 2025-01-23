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
                'user',
                openapi.IN_FORM,
                description='유저 아이디',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'frame',
                openapi.IN_FORM,
                description='프레임 아이디',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'custom_frame_title',
                openapi.IN_FORM,
                description='커스텀 프레임 제목',
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'custom_frame_img',
                openapi.IN_FORM,
                description='커스텀 프레임 이미지 파일',
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'is_shared',
                openapi.IN_FORM,
                description='공유 여부',
                type=openapi.TYPE_BOOLEAN,
                required=True
            ),
            openapi.Parameter(
                'is_bookmarked',
                openapi.IN_FORM,
                description='북마크 여부',
                type=openapi.TYPE_BOOLEAN,
                required=True
            ),
            openapi.Parameter(
                'is_deleted',
                openapi.IN_FORM,
                description='삭제 여부',
                type=openapi.TYPE_BOOLEAN,
                required=True
            )
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
            # POST 데이터 가져오기 (JSON 데이터가 아니라면 request.data 사용)
            custom_frame_title = request.data.get("custom_frame_title")
            is_shared = request.data.get("is_shared")
            is_shared = True if is_shared == "true" else False if is_shared == "false" else is_shared  # 변환 추가

            custom_frame_img = request.FILES.get("custom_frame_img")
            if not custom_frame_img:
                return Response({"code": "CSF_4002", "message": "이미지가 전송되지 않았습니다."}, status=400)

            # 이미지 파일 처리
            image_data = custom_frame_img.read()
            img = Image.open(BytesIO(image_data))
            custom_frame_img_name = f"custom_frame_{int(time.time())}.jpg"
            img_file = BytesIO()
            img.save(img_file, format="JPEG")
            img_file.seek(0)

            custom_frame_img_url = upload_file_to_s3(
                file=img_file,
                key=f"custom-frames/{custom_frame_img_name}",
                ExtraArgs={"ContentType": "image/jpeg", "ACL": "public-read"},
            )

            # 유저와 프레임 조회
            user_id = request.data.get("user")
            user = User.objects.filter(user_id=user_id).first()
            if not user:
                return Response({"code": "CSF_4041", "message": "해당 유저를 찾을 수 없습니다."}, status=404)

            frame_id = request.data.get("frame")
            frame = Frame.objects.filter(frame_id=frame_id).first()
            if not frame:
                return Response({"code": "CSF_4042", "message": "해당 프레임을 찾을 수 없습니다."}, status=404)

            # CustomFrame 생성
            custom_frame = CustomFrame.objects.create(
                user=user,
                frame=frame,
                custom_frame_title=custom_frame_title,
                custom_frame_url=custom_frame_img_url,
                is_shared=is_shared,
                is_bookmarked=False,
                is_deleted=False,
            )

            # 스티커 처리
            stickers = request.data.get("stickers", [])
            for sticker_data in stickers:
                sticker_id = sticker_data.get("sticker_id")
                sticker = Sticker.objects.filter(sticker_id=sticker_id).first()
                if not sticker:
                    logger.warning(f"스티커 ID {sticker_id}가 존재하지 않습니다.")
                    continue

                CustomFrameSticker.objects.create(
                    custom_frame=custom_frame,
                    sticker=sticker,
                    position_x=sticker_data.get("position_x"),
                    position_y=sticker_data.get("position_y"),
                    sticker_width=sticker_data.get("sticker_width"),
                    sticker_height=sticker_data.get("sticker_height"),
                    is_deleted=False,
                )

            return Response(
                {
                    "code": "CSF_2001",
                    "status": 201,
                    "message": "커스텀 프레임 생성 성공",
                    "data": {"custom_frame_id": custom_frame.custom_frame_id},
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"서버 오류: {str(e)}")
            return Response(
                {"code": "CSF_5001", "status": 500, "message": f"서버 오류: {str(e)}"},
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
                # GET 파라미터 가져오기
                sort_option = request.GET.get("sort", "latest")

                # 정렬 옵션에 따라 쿼리 실행
                if sort_option == "bookmarks":
                    custom_frames = CustomFrame.objects.filter(is_deleted=False).order_by("-bookmarks")
                else:  # 기본값: 최신순 정렬
                    custom_frames = CustomFrame.objects.filter(is_deleted=False).order_by("-created_at")

                # 조회된 커스텀 프레임이 없는 경우
                if not custom_frames.exists():
                    return Response(
                        {
                            "code": "CSF_4041",
                            "status": 404,
                            "message": "커스텀 프레임 목록 조회 실패",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )

                # 데이터 변환
                custom_frames_data = [
                    {
                        "customFrameId": customframe.custom_frame_id,
                        "customFrameTitle": customframe.custom_frame_title,
                        "customFrameUrl": customframe.custom_frame_url,
                        "bookmarks": customframe.bookmarks,
                        "created_at": customframe.created_at.isoformat(),
                    }
                    for customframe in custom_frames if customframe.is_shared is True
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


