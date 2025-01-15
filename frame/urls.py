from django.urls import path
from .views import CreateFrameView
from .views import FrameDetailView

urlpatterns = [
    path("", CreateFrameView.as_view(), name="frame-create"),
    path("<int:frameId>/", FrameDetailView.as_view(), name="frame-detail"),
]
