from rest_framework import serializers

from photo.models import Photo


class CreatePhotoSerializer(serializers.ModelSerializer):
    photoImg = serializers.FileField(write_only=True)
    photoUrl = serializers.CharField(read_only=True)
    class Meta:
        model = Photo
        fields = ['userId', 'photoId', 'photoImg', 'photoUrl']