# Generated by Django 4.1.7 on 2023-03-31 14:46

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_profile_header'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=cloudinary.models.CloudinaryField(blank=True, default='Default_Pic_lk0scq.webp', max_length=255, null=True, verbose_name='image'),
        ),
    ]
