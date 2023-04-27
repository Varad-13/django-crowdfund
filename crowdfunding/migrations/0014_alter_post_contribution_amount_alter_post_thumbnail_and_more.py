# Generated by Django 4.1.3 on 2023-04-14 08:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0013_transaction_post_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='contribution_amount',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
        migrations.AlterField(
            model_name='post',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='videos_uploaded', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]),
        ),
    ]