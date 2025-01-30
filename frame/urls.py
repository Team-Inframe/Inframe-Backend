from django.urls import path
from .views import CreateFrameView, CreateAiFrameView, FrameDetailView

urlpatterns = [
    path("", CreateFrameView.as_view(), name="frame-create"),
    path("/<int:frame_id>", FrameDetailView.as_view(), name="frame-detail"),
    path('/images', CreateAiFrameView.as_view(), name='create-frame-images'),
]
