# Generated by Django 5.1.4 on 2025-01-24 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_rename_user_user_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='username', max_length=20),
        ),
    ]
