from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from social.serializers import FollowersSerializer, LikeSerializer

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "bio",
            "get_avatar",
        ]


class UserSerializer(serializers.ModelSerializer):

    notifications = serializers.SerializerMethodField("num_notifications")
    messages = serializers.SerializerMethodField("num_messages")
    followers = FollowersSerializer(many=True)
    following = FollowersSerializer(many=True)
    likes = LikeSerializer(many=True)
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "following",
            "followers",
            "profile",
            "date_joined",
            "likes",
            "notifications",
            "messages",
        ]

    def num_notifications(self, user_object):
        user = User.objects.get(pk=user_object.pk)
        notifications = user.notification_to.all()
        return notifications.filter(user_has_seen=False).count()

    def num_messages(self, user_object):
        thread1 = user_object.my_threads.all()
        thread2 = user_object.threads.all()
        thread = thread1 | thread2
        return thread.filter(
            messages__is_read=False, messages__receiver_user=user_object
        ).count()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
            validated_data["password"],
        )

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
