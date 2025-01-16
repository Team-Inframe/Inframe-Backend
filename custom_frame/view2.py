
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
                            "customFrameTitle": "string",
                            "customFrameUrl": "string",
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

    def get(self, request, customFrameId):

        try :
            customFrame = CustomFrame.objects.get(pk=customFrameId)
            logger.info(f"customFrame:{customFrame}")
            response_data = {
                "code": "CSF_2001",
                "message": "커스텀 프레임 단일 조회 성공",
                "data": {
                    "customFrameTitle": customFrame.custom_frame_title,
                    "customFrameUrl": customFrame.custom_frame_url,
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
                                "customFrames": [
                                    {
                                    "customFrameId": 1,
                                    "customFrameTitle": "지브리st",
                                    "customFrameUrl": "https://example.com/frame1.png"
                                    },
                                    {
                                    "customFrameId": 2,
                                    "customFrameTitle": "귀여운st",
                                    "customFrameUrl": "https://example.com/frame2.png"
                                    }
                                ]
                            },
                            {
                                "date": "2025-01-14",
                                "customFrames": [
                                    {
                                    "customFrameId": 3,
                                    "customFrameTitle": "힐링st",
                                    "customFrameUrl": "https://example.com/frame3.png"
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
    def get(self, request, customFrameId):

        try:
            customFrame = CustomFrame.objects.get(pk=customFrameId)
            logger.info(f"customFrame:{customFrame}")
            response_data = {
                "code": "STG_2001",
                "message": "나의 커스텀 프레임 목록 조회 성공",
                "data": [
                    {
                        "date": customFrame.created_at,
                        "customFrames": [
                            {
                                "customFrameId": 1,
                                "customFrameTitle": customFrame.custom_frame_title,
                                "customFrameUrl": customFrame.custom_frame_url,
                            },
                            {
                                "customFrameId": 2,
                                "customFrameTitle": customFrame.custom_frame_title,
                                "customFrameUrl": customFrame.custom_frame_url,
                            }
                        ]
                    },
                    {
                        "date": customFrame.created_at,
                        "customFrames": [
                            {
                                "customFrameId": 3,
                                "customFrameTitle": customFrame.custom_frame_title,
                                "customFrameUrl": customFrame.custom_frame_url,
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
