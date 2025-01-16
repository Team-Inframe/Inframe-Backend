
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomFrame



import logging




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
    @swagger_auto_schema(
        operation_summary="나의 커스텀 프레임 목록 조회 API",
        operation_description="나의 커스텀 프레임 목록 조회",

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
                description="커스텀 프레임 단일 조회 실패",
                examples={
                    "application/json": {
                        "code": "STG_4001",
                        "status": 400,
                        "message": "나의 커스텀 프레임 목록 조회 실패"
                    }
                }
            ),
        },
    )
    def get(self, request, custom_frame_id):

        try:
            custom_frame = CustomFrame.objects.get(pk=custom_frame_id)
            logger.info(f"custom_frame:{custom_frame}")
            response_data = {
                "code": "STG_2001",
                "message": "나의 커스텀 프레임 목록 조회 성공",
                "data": [
                    {
                        "date": custom_frame.created_at,
                        "custom_frames": [
                            {
                                "custom_frameId": 1,
                                "custom_frame_title": custom_frame.custom_frame_title,
                                "custom_frame_url": custom_frame.custom_frame_url,
                            },
                            {
                                "custom_frameId": 2,
                                "custom_frame_title": custom_frame.custom_frame_title,
                                "custom_frame_url": custom_frame.custom_frame_url,
                            }
                        ]
                    },
                    {
                        "date": custom_frame.created_at,
                        "customFrames": [
                            {
                                "custom_frameId": 3,
                                "custom_frame_title": custom_frame.custom_frame_title,
                                "custom_frame_url": custom_frame.custom_frame_url,
                            }
                        ]
                    }
                ]
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error creating frame: {str(e)}")
            response_data = {
                "code": "STG_4001",
                "status": 400,
                "message": "나의 커스텀 프레임 목록 조회 실패"
            }

            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
