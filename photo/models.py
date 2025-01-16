from django.db import models
from user.models import User

class Photo(models.Model):
    photoId = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, db_column='userId')
    photoUrl = models.CharField(max_length=1000)
    createdAt = models.DateTimeField(auto_now_add=True)
    isDeleted = models.BooleanField(default=False)
    class Meta:
        db_table = 'photo'

