from rest_framework import serializers

from photo.models import Photo


class CreatePhotoSerializer(serializers.ModelSerializer):
    photo_img = serializers.FileField(write_only=True)
    photo_url = serializers.CharField(read_only=True)
    class Meta:
        model = Photo
        fields = ['photo_id', 'photo_img', 'photo_url']

class PhotoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            'photo_id', 'photo_url'
        ]