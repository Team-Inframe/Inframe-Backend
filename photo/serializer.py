from rest_framework import serializers

from photo.models import Photo


class CreatePhotoSerializer(serializers.ModelSerializer):
    photo_img = serializers.FileField(write_only=True)
    photo_url = serializers.CharField(read_only=True)
    location = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = Photo
        fields = ['photo_id', 'photo_img', 'photo_url', 'location']

class PhotoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['photo_id', 'photo_url', 'location']