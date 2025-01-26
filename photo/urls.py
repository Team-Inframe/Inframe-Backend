from django.urls import path

from photo.views import CreatePhotoView, PhotoListView, PhotoSingleView

urlpatterns = [
    path("", CreatePhotoView.as_view(), name="photo-create"),
    path("lists", PhotoListView.as_view(), name="photo-list"),
    path("<int:photo_id>", PhotoSingleView.as_view(), name="photo-single-view"),

]