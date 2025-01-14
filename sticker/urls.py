from django.urls import path

from sticker import views
from sticker.views import StickerView

urlpatterns = [
    path('', StickerView.as_view(), name='sticker'),
]