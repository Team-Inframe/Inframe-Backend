from django.db import models
from user.models import User


# Create your models here.


class Photo(models.Model):
    photoId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    photoUrl = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    isDeleted = models.BooleanField(default=False)
    class Meta:
        db_table = 'photo'  # 데이터베이스
    def __str__(self):

