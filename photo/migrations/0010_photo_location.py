# Generated by Django 5.1.4 on 2025-01-30 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photo', '0009_rename_photo_photo_photo_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
