from django.urls import path

from .view2 import CustomFrameDetailView, CustomMyFrameDetailView, MySavedFramesView, BookmarkView
from .views1 import CustomFrameCreateView,  CustomFrameListView

urlpatterns = [
  path("<int:custom_frame_id>", CustomFrameDetailView.as_view(), name = "custom_frames"),

  path("bookmark/",BookmarkView.as_view() , name = "bookmark"),
  path("myframes", CustomMyFrameDetailView.as_view() , name = "my_frames"),
  path("users/<int:user_id>", MySavedFramesView.as_view(), name="mySavedFrames"),

  #  path("")
  path("", CustomFrameCreateView.as_view(), name="custom-frame-create"),
  path("list", CustomFrameListView.as_view(), name="custom_frame_list"),  # 목록 조회 API 
]
