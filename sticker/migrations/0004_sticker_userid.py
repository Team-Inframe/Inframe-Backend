# Generated by Django 5.1.4 on 2025-01-16 07:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sticker', '0003_remove_sticker_userid'),
        ('user', '0004_rename_userid_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='sticker',
            name='userId',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='user.user'),
        ),
    ]
