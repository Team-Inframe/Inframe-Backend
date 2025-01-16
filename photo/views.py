from django.shortcuts import render
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.views import APIView

from photo.models import Photo


# Create your views here.

class CreatePhotoView(APIView):

    @swagger_auto_schema(

        operation_summary="Create Photo",
        operation_description="Create Photo",
        manual_parameters=[
            openapi.Parameter(

            )
        ]

    )

    def post(self, request):
