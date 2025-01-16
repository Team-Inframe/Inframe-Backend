from django.db import models

from user.models import User


class Sticker(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, db_column="userId")
    stickerUrl = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    isDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "sticker"