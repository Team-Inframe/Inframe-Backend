# Generated by Django 5.1.4 on 2025-01-16 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('frame', '0006_rename_id_frame_frame'),
    ]

    operations = [
        migrations.RenameField(
            model_name='frame',
            old_name='frame',
            new_name='frame_id',
        ),
    ]
