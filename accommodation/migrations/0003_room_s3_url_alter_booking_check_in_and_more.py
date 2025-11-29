
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accommodation', '0002_remove_room_s3_url_alter_room_image_booking'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='s3_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='check_in',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='booking',
            name='check_out',
            field=models.CharField(max_length=50),
        ),
    ]
