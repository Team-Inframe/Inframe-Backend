# Generated by Django 5.1.4 on 2025-01-17 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_frame', '0004_customframesticker'),
    ]

    operations = [
        migrations.AddField(
            model_name='customframe',
            name='bookmarks',
            field=models.IntegerField(default=0),
        ),
    ]
