from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, request
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomFrame, Sticker, CustomFrameSticker, Bookmark, User
from user.models import User
from frame.models import Frame
from .s3_utils import upload_file_to_s3
from io import BytesIO
from PIL import Image
import time
import logging
import json
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import redis
from django_redis import get_redis_connection
from django.shortcuts import get_object_or_404
from .serializer import CustomFrameSerializer
from django.db.models.functions import TruncDate

logger = logging.getLogger("inframe")
redis_conn = get_redis_connection("default")

import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

rain_frame = env('rain_frame')
snow_frame = env('snow_frame')
sun_frame = env('sun_frame')

snow_sticker_1 = env('snow_sticker_1')
snow_sticker_2 = env('snow_sticker_2')
snow_sticker_3 = env('snow_sticker_3')

rain_sticker_1 = env('rain_sticker_1')
rain_sticker_2 = env('rain_sticker_2')
rain_sticker_3 = env('rain_sticker_3')

sun_sticker_1 = env('sun_sticker_1')
sun_sticker_2 = env('sun_sticker_2')


class CustomFrameDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="커스텀 프레임 조회 API",
        operation_description="커스텀 프레임 단일 조회를 수행합니다.",
        responses={
            200: openapi.Response(
                description="커스텀 프레임 단일 조회 성공",
                examples={
                    "application/json": {
                        "code": "CSF_2001",
                        "message": "커스텀 프레임 단일 조회 성공",
                        "data": {
                            "customFrameTitle": "string",
                            "customFrameUrl": "string",
                            "frameId": 0,
                            "customFrameBg": "string",
                            "basicFrameId": 0,
                            "bookmarks": 0,
                            "stickers": [
                                {
                                    "stickerImgUrl": "string",
                                    "stickerX": 100,
                                    "stickerY": 200,
                                    "stickerWidth": 100,
                                    "stickerHeight": 100
                                },
                                {
                                    "stickerImgUrl": "string",
                                    "stickerX": 150,
                                    "stickerY": 250,
                                    "stickerWidth": 120,
                                    "stickerHeight": 120
                                }
                            ],
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="커스텀 프레임 단일 조회 실패",
                examples={
                    "application/json": {
                        "code": "CSF_4001",
                        "status": 400,
                        "message": "커스텀 프레임 단일 조회 실패"
                    }
                }
            ),
        },
    )
    def get(self, request, custom_frame_id):
        try:
            # 커스텀 프레임 조회
            custom_frame = CustomFrame.objects.get(pk=custom_frame_id)
            logger.info(f"custom_frame: {custom_frame}")

            # 연관된 스티커 조회
            customFrameStickers = CustomFrameSticker.objects.filter(custom_frame=custom_frame, is_deleted=False)

            sticker_list = [
                {
                    "stickerUrl": customFrameSticker.sticker.sticker_url,
                    "positionX": customFrameSticker.position_x,
                    "positionY": customFrameSticker.position_y,
                    "stickerWidth": customFrameSticker.sticker_width,
                    "stickerHeight": customFrameSticker.sticker_height,
                }
                for customFrameSticker in customFrameStickers
            ]

            # 응답 데이터 생성
            response_data = {
                "code": "CSF_2001",
                "status": 200,
                "message": "커스텀 프레임 단일 조회 성공",
                "data": {
                    "customFrameTitle": custom_frame.custom_frame_title,
                    "customFrameUrl": custom_frame.custom_frame_url,
                    "frameId": custom_frame.frame.frame_id,
                    "customFrameBg": custom_frame.frame.frame_bg,
                    "basicFrameId": custom_frame.frame.basic_frame_id,
                    "bookmarks": custom_frame.bookmarks,
                    "stickers": sticker_list,
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except CustomFrame.DoesNotExist:
            logger.error(f"CustomFrame with ID {custom_frame_id} not found.")
            response_data = {
                "code": "CSF_4001",
                "status": 404,
                "message": "커스텀 프레임 단일 조회 실패"
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving frame: {str(e)}")
            response_data = {
                "code": "CSF_5001",
                "status": 500,
                "message": "서버 오류 발생"
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomMyFrameDetailView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="나의 커스텀 프레임 목록 조회 API",
        operation_description="나의 커스텀 프레임 목록 조회",
        manual_parameters=[
            openapi.Parameter(
                name="user_id",
                in_=openapi.IN_QUERY,
                description="유저 아이디",
                type=openapi.TYPE_INTEGER,
                required=False,
            )
        ],
        responses={
            200: openapi.Response(
                description="나의 커스텀 프레임 목록 조회 성공",
                examples={
                    "application/json": {
                        "code": "STG_2001",
                        "message": "나의 커스텀 프레임 목록 조회 성공",
                        "data": [
                            {
                                "date": "2025-01-13",
                                "custom_frames": [
                                    {
                                        "custom_frame_id": 1,
                                        "custom_frame_title": "지브리st",
                                        "custom_frame_url": "https://example.com/frame1.png"
                                    },
                                    {
                                        "custom_frame_id": 2,
                                        "custom_frame_title": "귀여운st",
                                        "custom_frame_url": "https://example.com/frame2.png"
                                    }
                                ]
                            },
                            {
                                "date": "2025-01-14",
                                "custom_frames": [
                                    {
                                        "custom_frame_id": 3,
                                        "custom_frame_title": "힐링st",
                                        "custom_frame_url": "https://example.com/frame3.png"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            400: openapi.Response(
                description="나의 커스텀 프레임 목록 조회 실패",
                examples={
                    "application/json": {
                        "code": "STG_4001",
                        "status": 400,
                        "message": "나의 커스텀 프레임 목록 조회 실패"
                    }
                }
            ),
        }, request_body=None,
    )
    def get(self, request):
        user_id = request.query_params.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        frames = CustomFrame.objects.filter(user=user, is_deleted=False).annotate(
            date=TruncDate('created_at')
        ).order_by('-date')

        grouped_frames = {}
        for frame in frames:
            date = frame.date.strftime('%Y.%m.%d')
            if date not in grouped_frames:
                grouped_frames[date] = []
            serialized_frame = CustomFrameSerializer(frame).data
            grouped_frames[date].append(serialized_frame)

        data = [
            {
                "date": date,
                "frames": frames
            } for date, frames in grouped_frames.items()
        ]

        return Response({
            "code": "STG_2001",
            "status": 200,
            "message": "나의 커스텀 프레임 목록 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)


class MySavedFramesView(APIView):
    @swagger_auto_schema(
        operation_summary="내가 저장한 커스텀 프레임 목록 조회 API",
        operation_description="내가 저장한 커스텀 프레임 목록 조회 API",
        responses={
            200: openapi.Response(
                description="Success",
                examples={
                    "application/json": {
                        "code": "STG_2001",
                        "message": "내가 저장한 프레임 목록 조회 성공",
                        "data": [
                            {
                                "date": "2023.01.01",
                                "frames": [
                                    {
                                        "id": 1,
                                        "name": "Frame Name",
                                        "description": "Frame Description",
                                        "created_at": "2023-01-01T12:34:56Z",
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            404: openapi.Response(
                description="User not found",
                examples={
                    "application/json": {
                        "detail": "Not found."
                    }
                }
            )
        },
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_PATH,
                description="The ID of the user whose frames are being fetched",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, user_id=user_id)

        bookmarks = Bookmark.objects.filter(user=user, is_deleted=False).select_related('custom_frame')

        grouped_frames = {}
        for bookmark in bookmarks:
            frame = bookmark.custom_frame
            logger.info(f"custom_frame: {frame}")
            date = frame.created_at.date().strftime('%Y.%m.%d')  # 날짜 형식 변환
            if date not in grouped_frames:
                grouped_frames[date] = []

            serialized_frame = CustomFrameSerializer(frame).data
            grouped_frames[date].append(serialized_frame)

        # 최신순 정렬
        sorted_grouped_frames = sorted(grouped_frames.items(), key=lambda x: x[0], reverse=True)

        data = [
            {
                "date": date,
                "frames": frame_list
            } for date, frame_list in sorted_grouped_frames
        ]

        return Response({
            "code": "STG_2001",
            "status": 200,
            "message": "내가 저장한 프레임 목록 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)


class BookmarkView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="커스텀 프레임 북마크",
        operation_description="커스텀 프레임 북마크",
        manual_parameters=[
            openapi.Parameter(
                name="user_id",
                in_=openapi.IN_FORM,
                description="유저 ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                name="custom_frame_id",
                in_=openapi.IN_FORM,
                description="커스텀 프레임 ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            )
        ],
        responses={
            200: openapi.Response(
                description="커스텀 프레임 북마크 성공",
                examples={
                    "code": "CSF_2001",
                    "status": 200,
                    "data": {
                        "is_bookmarked": True
                    },
                    "message": "커스텀 프레임 북마크 성공",
                }
            ),
            400: openapi.Response(
                description="커스텀 프레임 북마크 실패",
                examples={
                    "application/json": {
                        "code": "CSF_4041",
                        "status": 404,
                        "message": "커스텀 프레임 북마크 실패"
                    }
                }
            ),
        },
    )
    def post(self, request):
        user_id = request.data.get("user_id")
        custom_frame_id = request.data.get("custom_frame_id")
        logger.info(f"custom_frame_id1: {custom_frame_id}")

        if not user_id:
            return Response(
                {"code": "CSF_4001", "message": "user_id가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not custom_frame_id:
            return Response(
                {"code": "CSF_4002", "message": "custom_frame_id가 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, user_id=user_id)
        custom_frame = get_object_or_404(CustomFrame, custom_frame_id=custom_frame_id)
        logger.info(f"custom_frame_id2: {custom_frame_id}")

        redis_key = "custom_frame_bookmarks"

        if not Bookmark.objects.filter(user=user, custom_frame=custom_frame).exists():
            Bookmark.objects.create(user=user, custom_frame=custom_frame)
            custom_frame.bookmarks += 1
            custom_frame.save(update_fields=['bookmarks'])
            redis_conn.zincrby(redis_key, 1, custom_frame_id)
            return Response(
                {
                    "code": "CSF_2001",
                    "status": 201,
                    "data": {
                        "is_bookmarked": True
                    },
                    "message": "북마크 저장 성공",
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            Bookmark.objects.filter(user_id=user_id, custom_frame=custom_frame).delete()
            custom_frame.bookmarks -= 1
            custom_frame.save(update_fields=['bookmarks'])
            redis_conn.zincrby(redis_key, -1, custom_frame_id)  # Redis 값 감소
            return Response(
                {
                    "code": "CSF_2002",
                    "status": 200,
                    "data": {
                        "is_bookmarked": False
                    },
                    "message": "북마크 삭제 성공",
                },
                status=status.HTTP_200_OK,
            )


class CustomFrameCreateView(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    @swagger_auto_schema(
        operation_summary="커스텀 프레임 생성 API",
        operation_description="form-data로 커스텀 프레임을 생성합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='사용자 아이디'),
                'frame_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='프레임 아이디'),
                'custom_frame_title': openapi.Schema(type=openapi.TYPE_STRING, description='커스텀 프레임 제목'),
                'custom_frame_img_url': openapi.Schema(type=openapi.TYPE_STRING, description='커스텀 프레임 이미지'),
                'is_shared': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='공유 여부'),
                'stickers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'sticker_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='스티커 ID'),
                            'position_x': openapi.Schema(type=openapi.TYPE_NUMBER, description='스티커 X 좌표'),
                            'position_y': openapi.Schema(type=openapi.TYPE_NUMBER, description='스티커 Y 좌표'),
                            'sticker_width': openapi.Schema(type=openapi.TYPE_NUMBER, description='스티커 너비'),
                            'sticker_height': openapi.Schema(type=openapi.TYPE_NUMBER, description='스티커 높이'),

                        }
                    ),
                    description='스티커 정보 배열'
                ),
            },
            required=['user_id', 'frame_id'],  # 필수 필드
        ),
    )
    def post(self, request):
        try:
            # 요청 데이터 검증
            custom_frame_title = request.data.get("custom_frame_title")

            is_shared = request.data.get("is_shared")
            if isinstance(is_shared, str):
                is_shared = is_shared.lower() in ["true", "1"]
            elif not isinstance(is_shared, bool):
                return Response({"code": "CSF_4004", "message": "is_shared 값이 잘못되었습니다."}, status=400)

            custom_frame_img = request.data.get("custom_frame_img_url")
            if not custom_frame_img:
                return Response({"code": "CSF_4002", "message": "이미지가 전송되지 않았습니다."}, status=400)

            # 유저와 프레임 조회
            user_id = request.data.get("user_id")
            user = User.objects.filter(user_id=user_id).first()
            if not user:
                return Response({"code": "CSF_4041", "message": "해당 유저를 찾을 수 없습니다."}, status=404)

            frame_id = request.data.get("frame_id")
            frame = Frame.objects.filter(frame_id=frame_id).first()

            if not frame:
                return Response({"code": "CSF_4042", "message": "해당 프레임을 찾을 수 없습니다."}, status=404)

            # CustomFrame 생성
            custom_frame = CustomFrame.objects.create(
                user=user,
                frame=frame,
                custom_frame_title=custom_frame_title,
                custom_frame_url=custom_frame_img,
                is_shared=is_shared,
            )

            # 스티커 처리
            stickers = request.data.get("stickers", [])
            if isinstance(stickers, str):
                stickers = json.loads(stickers)

            failed_stickers = []
            for sticker_data in stickers:
                sticker_id = sticker_data.get("sticker_id")
                sticker = Sticker.objects.filter(sticker_id=sticker_id).first()
                if not sticker:
                    failed_stickers.append(sticker_id)
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

            # 응답 데이터
            response_data = {
                "code": "CSF_2001",
                "status": 201,
                "message": "커스텀 프레임 생성 성공",
                "data": {"custom_frame_id": custom_frame.custom_frame_id},
            }

            if failed_stickers:
                response_data["failed_stickers"] = failed_stickers

            return Response(response_data, status=status.HTTP_201_CREATED)

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
                    "created_at": customframe.created_at.date().strftime('%Y.%m.%d'),
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


class CustomFrameHotView(APIView):
    @swagger_auto_schema(
        operation_summary="핫한 커스텀 프레임 목록 조회",
        operation_description="핫한 커스텀 프레임 4개를 조회합니다.",
        responses={
            200: openapi.Response(
                description="핫한 커스텀 프레임 목록 조회",
                examples={
                    "application/json": [
                        {"custom_frame_id": "1", "custom_frame_title": "Frame 1", "custom_frame_url": "Frame 1",
                         "bookmarks": 4},
                        {"custom_frame_id": "2", "custom_frame_title": "Frame 2", "custom_frame_url": "Frame 2",
                         "bookmarks": 3},
                        {"custom_frame_id": "3", "custom_frame_title": "Frame 3", "custom_frame_url": "Frame 3",
                         "bookmarks": 2},
                        {"custom_frame_id": "4", "custom_frame_title": "Frame 4", "custom_frame_url": "Frame 4",
                         "bookmarks": 1},
                    ]
                }
            )
        }
    )
    def get(self, request):
        hot_custom_frames = get_hot_custom_frames()
        return Response(hot_custom_frames)


def get_hot_custom_frames():
    data = []
    for i in range(1, 5):
        custom_frame_data = redis_conn.hgetall(f"hot_custom_frame:{i}")
        custom_frame_data = {key.decode("utf-8"): value.decode("utf-8") for key, value in custom_frame_data.items()}
        data.append(custom_frame_data)
    return data


class CustomFrameUploadAPIView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="커스텀 프레임 이미지 업로드 API",
        operation_description="커스텀 프레임 이미지 Url 반환.",
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                description="업로드할 파일",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="파일 업로드 성공",
                examples={
                    "application/json": {
                        "code": "FILE_2001",
                        "message": "파일 업로드 성공",
                        "data": {
                            "file_url": "string"
                        }
                    }
                },
            ),
            400: openapi.Response(
                description="파일 업로드 실패 (요청 오류)",
                examples={
                    "application/json": {
                        "code": "FILE_4001",
                        "message": "파일이 전송되지 않았습니다."
                    }
                },
            ),
            500: openapi.Response(
                description="서버 오류 발생",
                examples={
                    "application/json": {
                        "code": "FILE_5001",
                        "message": "서버 오류 발생"
                    }
                },
            ),
        },
    )
    def post(self, request):
        try:
            uploaded_file = request.FILES.get("file")
            if not uploaded_file:
                return Response(
                    {"code": "FILE_4001", "message": "파일이 전송되지 않았습니다."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            file_name = f"uploaded_file_{int(time.time())}_{uploaded_file.name}"

            file_url = upload_file_to_s3(
                file=uploaded_file,
                key=f"uploads/{file_name}",
                ExtraArgs={"ContentType": uploaded_file.content_type, "ACL": "public-read"},
            )

            if not file_url:
                return Response(
                    {
                        "code": "FILE_5002",
                        "message": "파일 업로드 실패",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {
                    "code": "FILE_2001",
                    "message": "파일 업로드 성공",
                    "data": {"file_url": file_url},
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {
                    "code": "FILE_5001",
                    "message": f"서버 오류 발생: {str(e)}",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WeatherFrameView(APIView):
    @swagger_auto_schema(
        operation_summary="날씨 프레임 조회",
        operation_description="날씨 조건에 맞는 프레임과 스티커를 조회하는 API",
        manual_parameters=[
            openapi.Parameter('weather_condition', openapi.IN_QUERY, description="날씨 조건 (예: Clear, Rain, Snow 등)",
                              type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="날씨 프레임 목록 조회 성공",
                examples={
                    "application/json": {
                        "code": "WEA_2001",
                        "status": 200,
                        "message": "날씨 프레임 목록 조회 성공",
                        "data": {
                            "customFrameImg": "비 프레임 이미지 URL",
                            "stickers": [
                                {
                                    "sticker_img_url": "sticker_1_img_url",
                                    "sticker_x": 100,
                                    "sticker_y": 100,
                                    "sticker_width": 100,
                                    "sticker_height": 100
                                }
                            ]
                        }
                    }
                }
            )
        }
    )
    def get(self, request):
        weather_condition = request.GET.get('weather_condition')

        custom_frame_data = self.get_custom_frame_data(weather_condition)

        return Response(
            {
                "code": "WEA_2001",
                "status": 200,
                "message": "날씨 프레임 목록 조회 성공",
                "data": custom_frame_data,
            },
            status=status.HTTP_200_OK,
        )

    def get_custom_frame_data(self, weather_condition):
        if weather_condition in ['Thunderstorm', 'Rain', 'Drizzle']:
            custom_frame_img = rain_frame
            stickers = self.get_stickers_for_rain()

        elif weather_condition == 'Snow':
            custom_frame_img = snow_frame
            stickers = self.get_stickers_for_snow()

        elif weather_condition == 'Clear':
            custom_frame_img = sun_frame
            stickers = self.get_stickers_for_clear()

        if custom_frame_img:
            return {
                "customFrameImg": custom_frame_img,
                "stickers": stickers
            }
        return None

    def get_stickers_for_rain(self):
        return [
            {
                "sticker_img_url": rain_sticker_1,
                "sticker_x": 100,
                "sticker_y": 100,
                "sticker_width": 100,
                "sticker_height": 100
            },
            {
                "sticker_img_url": rain_sticker_2,
                "sticker_x": 200,
                "sticker_y": 200,
                "sticker_width": 200,
                "sticker_height": 200
            },
            {
                "sticker_img_url": rain_sticker_3,
                "sticker_x": 300,
                "sticker_y": 300,
                "sticker_width": 300,
                "sticker_height": 300
            },
        ]

    def get_stickers_for_snow(self):
        return [
            {
                "sticker_img_url": snow_sticker_1,
                "sticker_x": 100,
                "sticker_y": 100,
                "sticker_width": 100,
                "sticker_height": 100
            },
            {
                "sticker_img_url": snow_sticker_2,
                "sticker_x": 200,
                "sticker_y": 200,
                "sticker_width": 200,
                "sticker_height": 200
            },
            {
                "sticker_img_url": snow_sticker_3,
                "sticker_x": 300,
                "sticker_y": 300,
                "sticker_width": 300,
                "sticker_height": 300
            },
        ]

    def get_stickers_for_clear(self):
        return [
            {
                "sticker_img_url": sun_sticker_1,
                "sticker_x": 100,
                "sticker_y": 100,
                "sticker_width": 100,
                "sticker_height": 100
            },
            {
                "sticker_img_url": sun_sticker_2,
                "sticker_x": 200,
                "sticker_y": 200,
                "sticker_width": 200,
                "sticker_height": 200
            },
        ]