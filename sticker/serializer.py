from rest_framework import serializers
from sticker.models import Sticker


class CreateStickerSerializer(serializers.ModelSerializer):
    prompt = serializers.CharField(required=False, allow_blank=True)
    uploaded_image = serializers.CharField(required=False, allow_blank=True)
    sticker_url = serializers.CharField(read_only=True)
    class Meta:
        model = Sticker
        fields = ['prompt', 'uploaded_image', 'sticker_url']

    def validate(self, data):
        if not data.get('prompt') and not data.get('uploaded_image'):
            raise serializers.ValidationError("텍스트 또는 파일을 제공해주세요.")
        return data