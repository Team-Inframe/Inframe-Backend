from django.urls import path
from .view2 import CustomFrameDetailView, CustomMyFrameDetailView
from .views1 import CustomFrameCreateView

urlpatterns = [
  #  path("")
    path("<int:custom_frame_id>/", CustomFrameDetailView.as_view(), name = "custom_frames"),
  #  path("")
  #  path("bookmark/", , name = "bookmark"),
    path("myframes/<int:custom_frame_id>/", CustomMyFrameDetailView.as_view() , name = "my_frames"),
  #  path("mySavedFrames/", , name="mySavedFrames"),
  #  path("")
  path("", CustomFrameCreateView.as_view(), name="custom-frame-create"),
]
