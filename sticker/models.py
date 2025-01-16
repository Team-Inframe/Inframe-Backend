from django.db import models

from user.models import User


class Sticker(models.Model):
    sticker_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sticker_url = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = "sticker"