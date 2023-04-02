import Levenshtein
from django.contrib.auth.models import User
from knox.models import AuthToken
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
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
        profile = Profile.objects.create(user=user)
        profile.save()
        return Response(
            {
                # "user": UserSerializer(
                #     user, context=self.get_serializer_context()
                # ).data,
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


@api_view(["GET"])
def is_used(request):
    print(request.query_params)
    if request.query_params.get("username"):
        try:
            User.objects.get(username=request.query_params.get("username"))
            recommendations = user_recommendation(request.query_params.get("username"))
            return Response(
                {"recommendations": recommendations}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response({"recommendations": []}, status=status.HTTP_200_OK)
    else:
        try:
            User.objects.get(email=request.query_params.get("email"))
            return Response({"isEmailTaken": 1}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"isEmailTaken": 0}, status=status.HTTP_200_OK)


def user_recommendation(current_username):
    ## adds variants of username
    variations = (
        [current_username + str(i) for i in range(10)]
        + [current_username.replace("o", "0")]
        + [current_username.replace("l", "1")]
        + [current_username.replace("i", "1")]
        + [current_username.replace("e", "3")]
        + [current_username.replace("s", "5")]
        + [current_username + word for word in ["_dev", "_coder", "_geek"]]
    )
    variations = set(variations)
    variations.discard(current_username)  # exclude current username and

    # Calculate similarity scores
    scores = [
        (username, Levenshtein.distance(current_username, username))
        for username in variations
    ]
    sorted_scores = sorted(scores, key=lambda x: x[1])

    recommendations = [s[0] for s in sorted_scores[1:4]]  # choose top 3
    return recommendations
