from django.db import models
from django.db.models import AutoField
from user.models import User
from frame.models import Frame



# Create your models here.

class CustomFrame(models.Model):
    custom_frame = AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    frame = models.ForeignKey(Frame, on_delete=models.CASCADE)
    custom_frame_title = models.CharField(max_length=30)
    custom_frame_url = models.CharField(max_length=255)
    is_shared = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


    class Meta:
        db_table = 'custom_frames'  # 데이터베이스 테이블 이름