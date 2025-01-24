from rest_framework import serializers
from .models import Frame


class FrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Frame
        fields = ['frame_id', 'frame_url', 'frame_bg', 'basic_frame_id']


class CreateFrameRequestSerializer(serializers.Serializer):
    frame_url = serializers.URLField(required=True)

class CreateFrameImgSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=False, allow_blank=True)
    frame_ai_url = serializers.CharField(read_only=True)

