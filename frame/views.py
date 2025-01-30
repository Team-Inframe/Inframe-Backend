import time
from datetime import datetime
from io import BytesIO
import random
from deep_translator import GoogleTranslator
from openai import OpenAI
client = OpenAI()

import requests
from PIL import Image
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from sticker.serializer import CreateStickerSerializer
from .models import Frame
from .s3_utils import upload_file_to_s3
import logging
from rest_framework.parsers import MultiPartParser

from .serializers import CreateFrameImgSerializer

logger = logging.getLogger("inframe")


class CreateFrameView(APIView):
    # MultiPartParser를 통해 파일 업로드를 처리
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="프레임 생성 API",
        operation_description="form-data로 이미지 파일과 카메라 크기를 업로드하여 프레임을 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                'frame_url',
                openapi.IN_FORM,
                description='완성된 배경 프레임',
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'frame_bg',
                openapi.IN_FORM,
                description='배경 프레임의 배경 이미지 (파일)',
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'basic_frame_id',
                openapi.IN_FORM,
                description='베이직 프레임 아이디',
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="성공적으로 프레임 생성",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="응답 코드"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="응답 메시지"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "frame_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="프레임 ID"),
                                "frame_url": openapi.Schema(type=openapi.TYPE_STRING, description="프레임 이미지 URL"),
                                "frame_bg_url": openapi.Schema(type=openapi.TYPE_STRING, description="배경 이미지 URL"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="요청 데이터 오류",
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
        logger.info(f"Request Data: {request.data}")
        logger.info(f"Request Files: {request.FILES}")

        frame_bg = request.data.get("frame_bg")
        frame_url_file = request.FILES.get("frame_url")
        basic_frame_id = request.data.get("basic_frame_id")

        if not frame_bg or not frame_url_file:
            return Response(
                {
                    "code": "FRA_4002",
                    "status": 400,
                    "message": "프레임 또는 배경 이미지 누락",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if isinstance(frame_bg, str) and (frame_bg.startswith("http") or frame_bg.startswith("BG")):
                frame_bg = frame_bg
            else:
                frame_bg_file = request.FILES.get("frame_bg")
                if frame_bg_file:
                    bg_image_data = frame_bg_file.read()
                    bg_img = Image.open(BytesIO(bg_image_data))

                    if bg_img.mode == 'RGBA':
                        bg_img = bg_img.convert('RGB')

                    bg_filename = f"bg_{int(time.time())}.jpg"
                    bg_img_file = BytesIO()
                    bg_img.save(bg_img_file, format="JPEG")
                    bg_img_file.seek(0)

                    frame_bg = upload_file_to_s3(
                        file=bg_img_file,
                        key=f"background-frames/{bg_filename}",
                        ExtraArgs={
                            "ContentType": "image/jpeg",
                            "ACL": "public-read",
                        },
                    )
                    if not frame_bg:
                        return Response(
                            {
                                "code": "FRA_5001",
                                "status": 500,
                                "message": "배경 이미지 업로드 실패",
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                else:
                    return Response(
                        {
                            "code": "FRA_4003",
                            "status": 400,
                            "message": "frame_bg가 파일도 URL도 아님",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            frame_image_data = frame_url_file.read()
            frame_img = Image.open(BytesIO(frame_image_data))

            if frame_img.mode == 'RGBA':
                frame_img = frame_img.convert('RGB')

            frame_filename = f"frame_{int(time.time())}.jpg"
            frame_img_file = BytesIO()
            frame_img.save(frame_img_file, format="JPEG")
            frame_img_file.seek(0)

            frame_url = upload_file_to_s3(
                file=frame_img_file,
                key=f"basic-frames/{frame_filename}",
                ExtraArgs={
                    "ContentType": "image/jpeg",
                    "ACL": "public-read",
                },
            )
            if not frame_url:
                return Response(
                    {
                        "code": "FRA_5001",
                        "status": 500,
                        "message": "프레임 이미지 업로드 실패",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            frame = Frame.objects.create(
                frame_url=frame_url,
                frame_bg=frame_bg,
                basic_frame_id=basic_frame_id,
            )

            response_data = {
                "code": "FRA_2001",
                "status": 201,
                "message": "프레임 생성 성공",
                "data": {
                    "frame_id": frame.frame_id,
                    "frame_url": frame_url,
                    "frame_bg": frame_bg,
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error creating frame: {str(e)}")
            response_data = {
                "code": "FRA_5002",
                "status": 500,
                "message": f"프레임 생성 실패: {str(e)}",
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateAiFrameView(APIView):
    @swagger_auto_schema(
        operation_summary="초기 프레임 배경 생성 API",
        operation_description="초기 프레임 배경 생성 페이지",
        request_body=CreateFrameImgSerializer,
        responses={
            201: openapi.Response(
                description="초기 프레임 배경 생성 성공",
                examples={
                    "application/json": {
                        "code": "FRA_2011",
                        "status": 201,
                        "message": "초기 프레임 배경 생성 성공",
                        "frameAiUrl": "https://example.com/stickers/generated_background.png"
                    }
                }
            ),
            400: openapi.Response(
                description="초기 프레임 배경 생성 실패",
                examples={
                    "application/json": {
                        "code": "FRA_4001",
                        "status": 400,
                        "message": "초기 프레임 배경 생성 실패"
                    }
                }
            ),
        }
    )
    def post(self, request):
        serializer = CreateFrameImgSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "code": "FRA_4001",
                "status": 400,
                "message": "유효하지 않은 데이터입니다.",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        prompt = validated_data.get('prompt')

        if prompt:
            translator = GoogleTranslator(source='ko', target='en')
            english_prompt = translator.translate(prompt)

            detailed_prompt = self.example_view(english_prompt)
            if not detailed_prompt or not isinstance(detailed_prompt, str):
                raise ValueError("Detailed prompt must be a valid string.")

            response = client.images.generate(
                prompt=detailed_prompt,
                n=1,
                size="1024x1024"
            )
            generated_image_url = response.data[0].url

            generated_image = self.download_image(generated_image_url)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"ai-frames/{prompt[:30].replace(' ', '_')}_{timestamp}.png"

            frame_url = self.upload_to_s3(generated_image, file_name)

        else:
            return Response({
                "code": "FRA_4001",
                "status": 400,
                "message": "유효하지 않은 데이터입니다.",
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "code": "FRA_2001",
            "status": 201,
            "message": "초기 프레임 배경 생성 완료",
            "frame_ai_url": frame_url
        }, status=status.HTTP_201_CREATED)

    def download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)

    def upload_to_s3(self, image, file_name):
        from django.core.files.storage import default_storage
        file_path = default_storage.save(file_name, image)
        return default_storage.url(file_path)

    def example_view(self, prompt):
        # 랜덤 숫자 생성 (1, 2, 3 중 하나)
        i = random.randint(1, 3)

        # 영어 프롬프트가 "dog"이면 메시지 생성

        # 랜덤 값에 따른 메시지 생성
        if i == 1:
            message = f"Too many {prompt} are in the city. {prompt} are crowded. Top,bottom,frame covered with {prompt}"
        elif i == 2:
            message = f"Too many {prompt} are in the school. {prompt} are crowded. Top,bottom,frame covered with {prompt}"
        elif i == 3:
            message = f"Too many {prompt} are in the sea. {prompt} are crowded. Top,bottom,frame covered with {prompt}"
        else:
            message = "white."

        return message


class FrameDetailView(APIView):
    @swagger_auto_schema(
        operation_summary="초기 프레임 조회 API",
        operation_description="프레임 ID를 기반으로 초기 프레임 URL을 반환합니다.",
        responses={
            200: openapi.Response(
                description="초기 프레임 조회 성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "code": openapi.Schema(type=openapi.TYPE_STRING, description="응답 코드"),
                        "message": openapi.Schema(type=openapi.TYPE_STRING, description="응답 메시지"),
                        "data": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "frame_url": openapi.Schema(type=openapi.TYPE_STRING, description="프레임 URL"),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="초기 프레임 조회 실패",
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
    def get(self, request, frame_id):
        """
        초기 프레임 조회 API
        프레임 ID를 기반으로 초기 프레임 URL을 반환합니다.
        """
        try:
            frame = Frame.objects.get(pk=frame_id)
            logger.info(f"frame: {frame}")
            response_data = {
                "code": "FRA_2001",
                "status": 200,
                "message": "초기 프레임 조회 성공",
                "data": {
                    "frame_id" : frame.frame_id,
                    "frame_url": frame.frame_url,
                },
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error creating frame: {str(e)}")
            response_data = {
                "code": "FRA_5002",
                "status": 500,
                "message": f"프레임 생성 실패: {str(e)}",
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
