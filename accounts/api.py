from django.contrib.auth.models import User
from knox.models import AuthToken
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        Profile.objects.create(user=user).save()
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response(
            {
                "user": UserSerializer(
                    user, context=self.get_serializer_context()
                ).data,
                "token": AuthToken.objects.create(user)[1],
            }
        )


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class GetUserAPI(APIView):
    serializer_class = UserSerializer

    def get(self, request):
        user = User.objects.get(pk=request.query_params.get("profile_id"))
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UpdateProfileAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, formate=None):
        profile = Profile.objects.get(user=request.user)
        if request.FILES.get("avatar") is not None:
            profile.avatar = request.FILES.get("avatar")

        try:
            user = User.objects.filter(pk=self.request.user.id)
            user.update(username=request.data["username"])
        except KeyError:
            pass

        try:
            profile.bio = request.data["bio"]
        except KeyError:
            pass

        profile.save()
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
