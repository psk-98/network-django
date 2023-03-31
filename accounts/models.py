from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        User, null=True, on_delete=models.CASCADE, related_name="profile", unique=True
    )
    avatar = CloudinaryField(
        "image", default="Default_Pic_lk0scq.webp", blank=True, null=True
    )
    bio = models.CharField(null=True, blank=True, max_length=256)

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return ""

    def __str__(self):
        return self.user.username


User._meta.get_field("email")._unique = False
User._meta.get_field("email").blank = True
User._meta.get_field("email").null = True
