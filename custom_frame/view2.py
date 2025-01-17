

from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models.functions import TruncDate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, request
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomFrame, User
from django.shortcuts import get_object_or_404


import logging

from .serializer import CustomFrameSerializer

logger = logging.getLogger("inframe")


class CustomFrameDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="커스텀 프레임 조회 API",
        operation_description="커스텀 프레임 조회 .",

        responses={
            200: openapi.Response(
                description="커스텀 프레임 단일 조회 성공",
                examples={
                    "application/json": {
                        "code": "CSF_2001",
                        "message": "커스텀 프레임 단일 조회 성공",
                        "data": {
                            "date": "2025-01-13",
                            "custom_frame_title": "string",
                            "custom_frame_url": "string",
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



        try :
            custom_frame = CustomFrame.objects.get(pk=custom_frame_id)
            logger.info(f"custom_frame:{custom_frame}")
            response_data = {
                "code": "CSF_2001",
                "message": "커스텀 프레임 단일 조회 성공",
                "data": {
                    "date": custom_frame.created_at.strftime("%Y-%m-%d"),
                    "custom_frame_title": custom_frame.custom_frame_title,
                    "custom_frame_url": custom_frame.custom_frame_url,
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error creating frame: {str(e)}")
            response_data = {
                "code": "CSF_4001",
                "status": 400,
                "message": "커스텀 프레임 단일 조회 실패"
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
        },request_body=None,
    )
    def get(self, request):
        user_id = request.query_params.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        frames = CustomFrame.objects.filter(user=user, is_deleted=False).annotate(
            date=TruncDate('created_at')
        ).order_by('date')

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
            "message": "나의 커스텀 프레임 목록 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)

class MySavedFramesView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="내가 저장한 커스텀 프레임 목록 조회 API",
        operation_description="내가 저장한 프레임 목록 조회 ",
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
                description="내가 저장한 프레임 목록 조회 성공",
                examples={
                    "application/json": {
                        "code": "STG_2001",
                        "message": "내가 저장한 프레임 목록 조회 성공",
                        "data": {
                            "custom_frames": [
                                {   "date": "2025-01-13",
                                    "custom_frame_id": 0,
                                    "custom_frame_title": "string",
                                    "custom_frame_url": "string",
                                },
                                {   "date": "2025-01-13",
                                    "custom_frame_id": 0,
                                    "custom_frame_title": "string",
                                    "custom_frame_url": "string",
                                },
                                {   "date": "2025-01-13",
                                    "custom_frame_id": 0,
                                    "custom_frame_title": "string",
                                    "custom_frame_url": "string",
                                },
                            ],
                        },
                    }
                }
            ),
            400: openapi.Response(
                description="내가 저장한 프레임 목록 조회 실패",
                examples={
                    "application/json": {
                        "code": "STG_4001",
                        "status": 400,
                        "message": "내가 저장한 프레임 목록 조회 실패"
                    }
                }
            ),
        },request_body=None,
    )
    def get(self, request):

        user_id = request.query_params.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        frames = CustomFrame.objects.filter(user=user, is_deleted=False).annotate(
            date=TruncDate('created_at')
        ).order_by('date')

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
            "message": "내가 저장한 프레임 목록 조회 성공",
            "data": data
        }, status=status.HTTP_200_OK)

