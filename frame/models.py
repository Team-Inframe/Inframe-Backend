from django.db import models

class Frame(models.Model):
    frame_id = models.AutoField(primary_key=True)
    frame_url = models.URLField()
    frame_bg = models.CharField(max_length=512)
    basic_frame_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'frames'

    def __str__(self):
        return f"Frame {self.frame_id}: {self.frame_url}"
