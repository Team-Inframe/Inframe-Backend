from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_frame', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customframe',
            old_name='createdAt',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='customFrame',
            new_name='custom_frame',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='customFrameTitle',
            new_name='custom_frame_title',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='customFrameUrl',
            new_name='custom_frame_url',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='frameId',
            new_name='frame',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='bookmark',
            new_name='is_bookmarked',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='isDeleted',
            new_name='is_deleted',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='isShared',
            new_name='is_shared',
        ),
        migrations.RenameField(
            model_name='customframe',
            old_name='userId',
            new_name='user',
        ),
    ]
