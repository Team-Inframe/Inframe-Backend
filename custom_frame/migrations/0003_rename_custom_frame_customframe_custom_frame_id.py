# Generated by Django 5.1.4 on 2025-01-16 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_frame', '0002_rename_createdat_customframe_created_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customframe',
            old_name='custom_frame',
            new_name='custom_frame_id',
        ),
    ]
