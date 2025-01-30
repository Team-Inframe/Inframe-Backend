from django.urls import path

from sticker import views
from sticker.views import StickerView, StickerListView

urlpatterns = [
    path('', StickerView.as_view(), name='sticker'),
    path('/list', StickerListView.as_view(), name='sticker-list'),
]