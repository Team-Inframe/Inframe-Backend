from django.db import models

class Frame(models.Model):
    frame_id = models.AutoField(primary_key=True)
    frame_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    camera_width = models.IntegerField()
    camera_height = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'frames'

    def __str__(self):
        return f"Frame {self.frame_id}: {self.frame_url}"
