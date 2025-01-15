import json
from rest_framework import serializers
from .models import Frame


class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = ['frame_id', 'frame_url', 'camera_width', 'camera_height']


class CreateFrameRequestSerializer(serializers.Serializer):
    frameImg = serializers.FileField(required=True)  # 이미지 파일 필드
    cameraWidth = serializers.IntegerField(required=True)  # 카메라 가로 크기 필드
    cameraHeight = serializers.IntegerField(required=True)  # 카메라 세로 크기 필드
    
    def validate(self, data):
        # 카메라 너비와 높이가 모두 존재하는지 확인
        if not data.get('cameraWidth') or not data.get('cameraHeight'):
            raise serializers.ValidationError("카메라 너비와 높이는 필수 항목입니다.")
        return data
