# Generated by Django 4.1.7 on 2023-03-15 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0015_alter_follow_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created',)},
        ),
    ]