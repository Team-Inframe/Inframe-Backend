
from django.urls import path
from .view2 import CustomFrameDetailView, CustomMyFrameDetailView

urlpatterns = [
  #  path("")
    path("<int:customFrameId>/", CustomFrameDetailView.as_view(), name = "customFrames"),
  #  path("")
  #  path("bookmark/", , name = "bookmark"),
    path("myframes/<int:customFrameId>/", CustomMyFrameDetailView.as_view() , name = "myFrames"),
  #  path("mySavedFrames/", , name="mySavedFrames"),
  #  path("")

]