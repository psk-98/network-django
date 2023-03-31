from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import Profile

from .models import (
    Comment,
    Follow,
    Like,
    Message,
    Notification,
    Post,
    PostMedia,
    Thread,
)


# filter the user info passed
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["get_avatar", "bio"]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "profile"]


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ["get_media", "media_type"]


class PostSerializer(serializers.ModelSerializer):
    num_comments = serializers.SerializerMethodField("get_comments")
    num_likes = serializers.SerializerMethodField("get_likes")
    author = UserSerializer()
    post_media = PostMediaSerializer(many=True)

    class Meta:
        model = Post
        depth = 1
        fields = "__all__"

    def get_comments(self, post_object):
        return post_object.comments.count()

    def get_likes(self, post_object):
        return post_object.likes.count()


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        depth = 1
        fields = ["id"]


class FollowSerializer(serializers.ModelSerializer):
    user = ProfileSerializer()
    following = ProfileSerializer()

    class Meta:
        model = Follow
        fields = "__all__"


class FollowersSerializer(serializers.ModelSerializer):
    following = UserSerializer()
    user = UserSerializer()

    class Meta:
        model = Follow
        fields = ["following", "user"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    num_likes = serializers.SerializerMethodField("get_likes")

    class Meta:
        model = Comment
        depth = 2
        fields = ["id", "body", "created", "author", "num_likes"]

    def get_likes(self, comment_object):
        return comment_object.likes.count()


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id"]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()

    class Meta:
        model = Notification
        fields = "__all__"


class PostDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    post_media = PostMediaSerializer(many=True)
    comments = CommentSerializer(many=True, read_only=True)
    num_likes = serializers.SerializerMethodField("get_likes")

    class Meta:
        model = Post
        depth = 1
        fields = "__all__"

    def get_likes(self, post_object):
        return post_object.likes.count()


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class ThreadsSerializer(serializers.ModelSerializer):
    latest_message = serializers.SerializerMethodField("get_latest_message")
    user = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Thread
        fields = "__all__"

    def get_latest_message(self, thread_object):
        message = Message.objects.filter(thread=thread_object).latest("created")
        return MessageSerializer(message).data


class ThreadSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    receiver = UserSerializer()
    messages = MessageSerializer(many=True)

    class Meta:
        model = Thread
        fields = "__all__"
