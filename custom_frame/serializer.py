from custom_frame.models import CustomFrame

from rest_framework import serializers

class CustomFrameSerializer(serializers.ModelSerializer):
    custom_frame_id = serializers.IntegerField(read_only=True)
    custom_frame_title = serializers.CharField(read_only=True)
    custom_frame_url=  serializers.CharField(read_only=True)

    class Meta:
        model = CustomFrame
        fields = ['custom_frame_id','custom_frame_title', 'custom_frame_url']

def validate_custom_frame(self, data):
    if not data.get('custom_id'):
        raise serializers.ValidationError("없는 아이디입니다.")
    return data

