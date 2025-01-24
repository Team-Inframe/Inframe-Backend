from http.client import responses

from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import user
from .models import User
from .serializer import SignupSerializer
from rest_framework.response import Response
import logging
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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
            f"{client_ip} POST /user/sign-up 201 Signup successful for user id: {user.user_id}"
        )

        return Response(
            {
                "user_id": user.user_id,
                "code": "MEM_2011",
                "status": 201,
                "message": "회원가입 성공",
            },
            status=status.HTTP_201_CREATED,
        )

class Login(APIView):
    @swagger_auto_schema(
        operation_summary="로그인 API",
        operation_description="사용자가 이메일과 비밀번호로 로그인하는 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={                
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User password"),
            },
            required=['email', 'password'],
        ),
        responses={
            201: openapi.Response(
                description="로그인 성공",
                examples={
                    "application/json": {
                        "code": "MEM_2001",
                        "data": {
                            "user_id": 1,
                            "username": "username",
                        },
                        "message": "로그인에 성공했습니다.",
                    }
                }
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={
                    "application/json": {
                        "status": "MEM_4001",
                        "message": "요청 데이터가 잘못되었습니다."
                    }
                }
            ),
            401: openapi.Response(
                description="로그인 실패",
                examples={
                    "application/json": {
                        "status": "MEM_4011",
                        "message": "이메일 또는 비밀번호가 올바르지 않습니다."
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        client_ip = request.META.get('REMOTE_ADDR', None)

        email = request.data.get('email', None)
        password = request.data.get('password', None)        

        if not email or not password:
            # 필수 필드 누락
            response_data = {
                "status": "MEM_4001",
                "message": "이메일과 비밀번호를 입력해주세요."
            }
            logger.warning(f"{client_ip} POST /login 400 Bad Request: 필수 데이터 누락")
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 이메일 유효성 검사
            validate_email(email)
        except ValidationError:
            response_data = {
                "status": "MEM_4002",
                "message": "유효하지 않은 이메일 형식입니다."
            }
            logger.warning(f"{client_ip} POST /login 400 Bad Request: 잘못된 이메일 형식")
            return Response(data=response_data, status=status.HTTP_400_BAD_REQUEST)

        # (여기서 유저 인증 로직 추가)
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            # 사용자 인증 실패
            response_data = {
                "status": "MEM_4011",
                "message": "이메일 또는 비밀번호가 올바르지 않습니다."
            }
            logger.warning(f"{client_ip} POST /login 401 Unauthorized: 사용자 인증 실패")
            return Response(data=response_data, status=status.HTTP_401_UNAUTHORIZED)

        # 로그인 성공
        response_data = {
            "code": "MEM_2001",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
            },
            "message": "로그인에 성공했습니다.",
        }
        logger.info(f"{client_ip} POST /login 201 Created: 로그인 성공 (User ID: {user.user_id})")
        return Response(data=response_data, status=status.HTTP_201_CREATED)
