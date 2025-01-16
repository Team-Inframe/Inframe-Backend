import os
import environ
from datetime import datetime
from io import BytesIO

import requests
from deep_translator import GoogleTranslator
from openai import OpenAI
from rest_framework.parsers import MultiPartParser, FormParser

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
                name="userId",
                in_=openapi.IN_FORM,
                description="유저 아이디",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                name="prompt",
                in_=openapi.IN_FORM,
                description="스티커를 생성할 텍스트 프롬프트",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                name="uploadedImage",
                in_=openapi.IN_FORM,
                description="스티커를 생성할 업로드된 이미지",
                type=openapi.TYPE_FILE,
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
                        "stickerUrl": "https://example.com/stickers/generated_sticker.png",
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
        request_body=None,
    )
    def post(self, request):
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
        uploaded_image = validated_data.get('uploadedImage')

        if bool(prompt) == bool(uploaded_image):
            return Response({
                "code": "STK_4001",
                "status": 400,
                "message": "텍스트 또는 파일 중 하나만 제공해야 합니다.",
            }, status=status.HTTP_400_BAD_REQUEST)

        if prompt:
            translator = GoogleTranslator(source='ko', target='en')
            english_prompt = translator.translate(prompt)

            detailed_prompt = f"{english_prompt}, a single main element, no background"

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

            file_name = f"stickers/{uploaded_image.name.split('.')[0]}_{timestamp}.png"
            sticker_url = self.upload_to_s3(bg_removed_image, file_name)
        else:
            return Response({
                "code": "STK_4001",
                "status": 400,
                "message": "텍스트 또는 파일을 제공해주세요.",
            }, status=status.HTTP_400_BAD_REQUEST)

        sticker = Sticker.objects.create(
            userId=request.user.id,
            stickerUrl=sticker_url
        )

        return Response({
            "code": "STK_2001",
            "status": 201,
            "message": "스티커 생성 완료",
            "stickerUrl": sticker.stickerUrl,
        }, status=status.HTTP_201_CREATED)

    def download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)

    def remove_background_with_api(self, image):
        url = env('REMOVE_BG_API_URL')

        headers = {"X-Api-Key": REMOVE_BG_API_KEY}
        if isinstance(image, BytesIO):
            files = {"image_file": ("input.png", image, "image/png")}
        else:
            files = {"image_file": (image.name, image.read(), image.content_type)}
        response = requests.post(url, headers=headers, files=files)

        if response.status_code != 200:
            raise Exception(f"Failed to remove background: {response.status_code} - {response.text}")
        return ContentFile(response.content, name="bg_removed.png")

    def upload_to_s3(self, image, file_name):

        from django.core.files.storage import default_storage
        file_path = default_storage.save(file_name, image)
        return default_storage.url(file_path)