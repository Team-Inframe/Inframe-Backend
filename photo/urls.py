from django.urls import path

from photo.views import CreatePhotoView, PhotoListView

urlpatterns = [
    path("", CreatePhotoView.as_view(), name="photo-create"),
    path("/lists", PhotoListView.as_view(), name="photo-list"),
]