import os
from collections import defaultdict

import environ
from datetime import datetime
from io import BytesIO

import requests
from deep_translator import GoogleTranslator
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from openai import OpenAI
from rest_framework.parsers import MultiPartParser, FormParser

from user.models import User

client = OpenAI()
from django.core.files.base import ContentFile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.settings import BASE_DIR
from sticker.models import Sticker
from sticker.serializer import CreateStickerSerializer

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
OPENAI_API_KEY = env('OPENAI_API_KEY')
REMOVE_BG_API_KEY = os.getenv('REMOVE_BG_API_KEY')

class StickerView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    @swagger_auto_schema(
        operation_summary="스티커 생성 API",
        operation_description="스티커 생성 페이지",
        manual_parameters=[
            openapi.Parameter(
                name="user_id",
                in_=openapi.IN_FORM,
                description="유저 아이디",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="prompt",
                in_=openapi.IN_FORM,
                description="스티커를 생성할 텍스트 프롬프트",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="uploaded_image",
                in_=openapi.IN_FORM,
                description="스티커를 생성할 업로드된 이미지",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            201: openapi.Response(
                description="스티커 생성 완료",
                examples={
                    "application/json": {
                        "code": "STK_2001",
                        "status": 201,
                        "message": "스티커 생성 완료",
                        "data": {
                            "sticker_id": 0,
                            "sticker_url": "https://example.com/stickers/generated_sticker.png",
                        }
                    }
                },
            ),
            400: openapi.Response(
                description="유효하지 않은 데이터입니다.",
                examples={
                    "application/json": {
                        "code": "STK_4001",
                        "status": 400,
                        "message": "스티커 생성 실패",
                    }
                },
            ),
        },
    )
    def post(self, request):
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        serializer = CreateStickerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "code": "STK_4001",
                "status": 400,
                "message": "유효하지 않은 데이터입니다.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        prompt = validated_data.get('prompt')
        uploaded_image = validated_data.get('uploaded_image')

        if bool(prompt) == bool(uploaded_image):
            return Response({
                "code": "STK_4001",
                "status": 400,
                "message": "텍스트 또는 파일 중 하나만 제공해야 합니다.",
            }, status=status.HTTP_400_BAD_REQUEST)

        if prompt:
            translator = GoogleTranslator(source='ko', target='en')
            english_prompt = translator.translate(prompt)

            detailed_prompt = f"happy {english_prompt}, minimalist sticker in cartoon style, emote cute, happy {english_prompt}"
            response = client.images.generate(
                prompt=detailed_prompt,
                n=1,
                size="1024x1024"
            )
            generated_image_url = response.data[0].url

            generated_image = self.download_image(generated_image_url)
            bg_removed_image = self.remove_background_with_api(generated_image)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"stickers/{prompt[:30].replace(' ', '_')}_{timestamp}.png"

            sticker_url = self.upload_to_s3(bg_removed_image, file_name)

        elif uploaded_image:
            bg_removed_image = self.remove_background_with_api(uploaded_image)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"stickers/sticker_{timestamp}.png"
            sticker_url = self.upload_to_s3(bg_removed_image, file_name)
        else:
            return Response({
                "code": "STK_4001",
                "status": 400,
                "message": "텍스트 또는 S3 URL을 제공해주세요.",
            }, status=status.HTTP_400_BAD_REQUEST)

        sticker = Sticker.objects.create(
            user_id=user.user_id,
            sticker_url=sticker_url
        )

        return Response({
            "code": "STK_2001",
            "status": 201,
            "message": "스티커 생성 완료",
            "data": {
                "sticker_id": sticker.sticker_id,
                "sticker_url": sticker.sticker_url,
            },
        }, status=status.HTTP_201_CREATED)

    def remove_background_with_api(self, image_url):
        url = env('REMOVE_BG_API_URL')
        headers = {"X-Api-Key": REMOVE_BG_API_KEY}
        payload = {"image_url": image_url}

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code != 200:
            raise Exception(f"Failed to remove background: {response.status_code} - {response.text}")

        return ContentFile(response.content, name="bg_removed.png")

    def upload_to_s3(self, image, file_name):
        from django.core.files.storage import default_storage
        file_path = default_storage.save(file_name, image)
        return default_storage.url(file_path)

    def download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)

    def remove_background_with_api(self, image_url):
        url = env('REMOVE_BG_API_URL')

        headers = {"X-Api-Key": REMOVE_BG_API_KEY}

        response = requests.get(image_url, stream=True)
        if response.status_code != 200:
            raise Exception(f"Failed to download image from S3: {response.status_code}")
        image = BytesIO(response.content)
        image.seek(0)

        files = {"image_file": ("input.png", image, "image/png")}
        response = requests.post(url, headers=headers, files=files)

        if response.status_code != 200:
            raise Exception(f"Failed to remove background: {response.status_code} - {response.text}")

        return ContentFile(response.content, name="bg_removed.png")

    def upload_to_s3(self, image, file_name):
        from django.core.files.storage import default_storage
        file_path = default_storage.save(file_name, image)
        return default_storage.url(file_path)


class StickerListView(APIView):
    @swagger_auto_schema(
        operation_summary="사용자별 스티커 목록 조회 API",
        operation_description="스티커 생성 페이지",
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
                description="스티커 조회 완료",
                examples={
                    "application/json": {
                        "code": "STK_2001",
                        "status": 200,
                        "message": "스티커 목록 조회 성공",
                        "data": [
                            {
                                "sticker_id": 1,
                                "sticker_url": "https://example.com/stickers/sticker_1.png",
                            },
                            {
                                "sticker_id": 2,
                                "sticker_url": "https://example.com/stickers/sticker_2.png",
                            },
                        ],
                    }
                },
            ),
            400: openapi.Response(
                description="유효하지 않은 데이터입니다.",
                examples={
                    "application/json": {
                        "code": "STK_4001",
                        "status": 400,
                        "message": "스티커 조회 실패",
                    }
                },
            ),
        },
    )
    def get(self, request):
        user_id = request.query_params.get("user_id")
        user = get_object_or_404(User, user_id=user_id)

        stickers = (
            Sticker.objects.filter(user=user, is_deleted=False)
            .values("sticker_id", "sticker_url", "created_at")
            .order_by("-created_at")
        )

        return Response({
            "code": "STK_2001",
            "status": 200,
            "message": "스티커 목록 조회 성공",
            "data": list(stickers)
        }, status=status.HTTP_200_OK)