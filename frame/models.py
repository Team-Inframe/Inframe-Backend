from django.db import models

class Frame(models.Model):
    frameId = models.AutoField(primary_key=True)  # 기본 키로 설정
    frameUrl = models.FileField(upload_to='frame/')
    createdAt = models.DateTimeField(auto_now_add=True)  # 레코드 생성 시 자동 설정
    cameraWidth = models.IntegerField()  # 카메라의 폭
    cameraHeight = models.IntegerField()  # 카메라의 높이
    isDeleted = models.BooleanField(default=False)  # 삭제 여부 플래그

    class Meta:
        db_table = 'frames'  # 데이터베이스 테이블 이름

    def __str__(self):
        return f"Frame {self.frameId}: {self.frameUrl}"
