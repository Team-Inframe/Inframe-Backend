from django.db import models

class Sticker(models.Model):
    id = models.AutoField(primary_key=True)
    stickerUrl = models.CharField(max_length=255)
    createdAt = models.DateTimeField(auto_now_add=True)
    isDeleted = models.BooleanField(default=False)

    class Meta:
        db_table = "sticker"