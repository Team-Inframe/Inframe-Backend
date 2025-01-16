
from django.urls import path
from .view2 import CustomFrameDetailView

urlpatterns = [
  #  path('')
    path("<int:customFrameId>/", CustomFrameDetailView.as_view(), name = "customFrames"),
  #  path('')
  #  path('bookmark/', , name = "bookmark"),
  #  path('myFrames/', , name = "myFrames"),
  #  path('mySavedFrames/', , name="mySavedFrames"),
  #  path('')

]