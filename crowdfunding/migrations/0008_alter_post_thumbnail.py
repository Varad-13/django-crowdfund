# Generated by Django 4.1.3 on 2023-04-12 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowdfunding', '0007_post_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='thumbnail',
            field=models.ImageField(null=True, upload_to='images/'),
        ),
    ]
