# Generated by Django 5.1.4 on 2025-01-16 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frame', '0004_alter_frame_frameurl'),
    ]

    operations = [
        migrations.RenameField(
            model_name='frame',
            old_name='cameraHeight',
            new_name='camera_height',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='cameraWidth',
            new_name='camera_width',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='createdAt',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='frameUrl',
            new_name='frame_url',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='frameId',
            new_name='id',
        ),
        migrations.RenameField(
            model_name='frame',
            old_name='isDeleted',
            new_name='is_deleted',
        ),
    ]
