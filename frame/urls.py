from django.urls import path
from .views import CreateFrameView, CreateAiFrameView

urlpatterns = [
    path('', CreateFrameView.as_view(), name='create-frame'),
    path('images/', CreateAiFrameView.as_view(), name='create-frame-images'),
]

