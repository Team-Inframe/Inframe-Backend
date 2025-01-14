from django.http import HttpResponse
from rest_framework.views import APIView


class StickerView(APIView):
    def get(self, request):
        return HttpResponse("Inframe World!")
