from rest_framework import serializers

from photo.models import Photo


class CreatePhotoSerializer(serializers.ModelSerializer):
    photo_img = serializers.FileField(write_only=True)
    photo_url = serializers.CharField(read_only=True)
    location = serializers.CharField(write_only=True, required=False)
    created_at = serializers.DateTimeField(read_only=True, format="%Y.%m.%d")  # 날짜 형식 지정

    class Meta:
        model = Photo
        fields = ['photo_id', 'photo_img', 'photo_url', 'location', 'created_at']

class PhotoListSerializer(serializers.ModelSerializer):
    location = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y.%m.%d")  # 날짜 형식 지정

    class Meta:
        model = Photo
        fields = ['photo_id', 'photo_url', 'location', 'created_at']