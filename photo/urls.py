from django.urls import path

from photo.views import CreatePhotoView

urlpatterns = [
    path("", CreatePhotoView.as_view(), name="photo-create"),
]