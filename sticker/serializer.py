from rest_framework import serializers
from sticker.models import Sticker


class CreateStickerSerializer(serializers.ModelSerializer):
    prompt = serializers.CharField(required=False, allow_blank=True)
    uploadedImage = serializers.FileField(required=False)
    stickerUrl = serializers.CharField(read_only=True)
    class Meta:
        model = Sticker
        fields = ['prompt', 'uploadedImage', 'stickerUrl']

    def validate(self, data):
        if not data.get('prompt') and not data.get('uploadedImage'):
            raise serializers.ValidationError("텍스트 또는 파일을 제공해주세요.")
        return data