from django.db import models
from django.db.models import AutoField
from user.models import User
from frame.models import Frame
from sticker.models import Sticker

# Create your models here.


class CustomFrame(models.Model):
    custom_frame_id = AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    custom_frame_title = models.CharField(max_length=30)
    custom_frame_url  = models.CharField(max_length=255)
    is_shared = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    bookmarks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "custom_frames"  # 데이터베이스 테이블 이름


class CustomFrameSticker(models.Model):
    custom_frame_sticker_id = models.AutoField(primary_key=True)
    custom_frame = models.ForeignKey(
        CustomFrame, on_delete=models.CASCADE, related_name="stickers"
    )
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE)
    position_x = models.FloatField()
    position_y = models.FloatField()
    sticker_width = models.FloatField()
    sticker_height = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "custom_frame_sticker"
