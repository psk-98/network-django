# Generated by Django 4.1.6 on 2023-03-07 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0013_alter_message_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('created',)},
        ),
        migrations.AlterField(
            model_name='message',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/message_images'),
        ),
    ]
