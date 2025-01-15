from django.urls import path
from .views import CreateFrameView

urlpatterns = [
    path('', CreateFrameView.as_view(), name='create-frame'),
]

