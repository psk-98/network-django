from cloudinary.models import CloudinaryField
from django.conf import settings
from django.db import models
from django.utils.text import slugify

MEDIA_CHOICES = (
    ("image", "image"),
    ("video", "video"),
)

NOTIFICATION_CHOICES = (
    ("DM", "DM"),
    ("FOLLOW", "FOLLOW"),
    ("LIKE", "LIKE"),
    ("COMMENT", "COMMENT"),
)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.CharField(max_length=280, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.id} {self.author} posted {self.body}"


class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name="post_media", on_delete=models.CASCADE)
    media = CloudinaryField("image")
    media_type = models.CharField(choices=MEDIA_CHOICES, max_length=20)

    def get_media(self):
        if self.media:
            return self.media.url
        return ""


class Follow(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followers",
        null=True,
        blank=True,
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.user} follows {self.following}"

    def is_valid_follow(self):
        return self.user != self.following


class Comment(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    body = models.CharField(max_length=280, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.id} {self.author} posted {self.body}"


class Notification(models.Model):
    notification_type = models.CharField(choices=NOTIFICATION_CHOICES, max_length=10)
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notification_to",
        on_delete=models.CASCADE,
        null=True,
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notification_from",
        on_delete=models.CASCADE,
        null=True,
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True)
    user_has_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return f"{self.from_user.username} {self.notification_type} {self.to_user.username}'s post or comment"


class Thread(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_threads",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="threads",
    )
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.make_slug())
        super().save(*args, **kwargs)

    def make_slug(self):
        return f"{self.user.username}-{self.receiver.username}"

    def __str__(self):
        return f"Message convo between {self.user} and {self.receiver}"


class Message(models.Model):
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="messages", blank=True, null=True
    )
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    receiver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    body = models.CharField(max_length=280, blank=False, null=False)
    image = CloudinaryField("image", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("created",)

    def __str__(self):
        return f"Message from {self.sender_user} to {self.receiver_user}"


class Like(models.Model):
    liker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="likes",
        on_delete=models.CASCADE,
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="likes", blank=True, null=True
    )
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="likes", blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created",)
