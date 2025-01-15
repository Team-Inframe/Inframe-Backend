from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializer import SignupSerializer
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)

class Sign_up(APIView):

    @swagger_auto_schema(
        operation_summary="회원가입 API",
        operation_description="Create a new user",
        request_body=SignupSerializer,
        responses={
            201: openapi.Response(
                description="회원가입 성공",
                examples={
                    "application/json": {
                        "code": "MEM_2001",
                        "message": "회원가입에 성공했습니다.",
                    }
                }
            ),
            400: openapi.Response(
                description="회원가입 실패",
                examples={
                    "application/json": {
                        "code": "MEM_4001",
                        "message": "회원가입에 실패했습니다."
                    }
                }
            ),
        }
    )
    def post(self, request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            logger.warning(
                f"{client_ip} POST /user/sign-up 400 Signup failed: {serializer.errors}"
            )
            return Response(
                {
                    "code": "MEM_4001",
                    "status": 400,
                    "message": "유효하지 않은 요청입니다.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        logger.info(
            f"{client_ip} POST /user/sign-up 201 Signup successful for user id: {user.id}"
        )

        return Response(
            {
                "user_id": user.id,
                "code": "MEM_2011",
                "status": 201,
                "message": "회원가입 성공",
            },
            status=status.HTTP_201_CREATED,
        )
