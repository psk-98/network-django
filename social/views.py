from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSerializer

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
from .serializers import (
    CommentSerializer,
    FollowersSerializer,
    LikeSerializer,
    MessageSerializer,
    NotificationSerializer,
    PostDetailSerializer,
    PostSerializer,
    ThreadSerializer,
    ThreadsSerializer,
)


@api_view(["GET"])
def all_posts(request):
    posts = Post.objects.order_by("-created").all()
    serializer = PostSerializer(posts, many=True)

    return Response(serializer.data)


class PostView(APIView):
    serializer_class = Post

    def get(self, request):
        try:
            post = Post.objects.get(pk=request.query_params.get("post_id"))
            serializer = PostDetailSerializer(post, many=False)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, formate=None):
        post = Post.objects.create(author=request.user, body=request.data["body"])
        post.save()
        if request.FILES.getlist("media"):
            for media in request.FILES.getlist("media"):
                post_meida = PostMedia.objects.create(
                    post=post, media=media, media_type="image"
                )
                post_meida.save()

        serializer = PostDetailSerializer(post, many=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        try:
            post = Post.objects.get(
                pk=request.query_params.get("id"), author=request.user
            )
            serializer = PostSerializer(instance=post, data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        try:
            post = Post.objects.get(
                author=request.user, pk=request.query_params.get("id")
            )
            post.delete()

            return Response(status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FollowView(APIView):
    serializer_class = FollowersSerializer

    def post(self, request, pk):

        recipient = User.objects.get(pk=pk)
        f = Follow.objects.create(user=request.user, following=recipient)
        f.save()
        n = Notification.objects.create(
            notification_type="FOLLOW", to_user=recipient, from_user=request.user
        )
        n.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        recipient = User.objects.get(pk=pk)
        f = Follow.objects.get(user=request.user, following=recipient)
        f.delete()

        return Response(status=status.HTTP_202_ACCEPTED)

    def get(self, request, pk):
        if request.query_params.get("isFollowers") == "1":
            user = User.objects.get(pk=pk)

            serializer = self.serializer_class(user.followers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            user = User.objects.get(pk=pk)
            serializer = self.serializer_class(user.following, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class LikeView(APIView):
    serializer_class = LikeSerializer

    def post(self, request):
        if request.data["isComment"] == True:
            comment = Comment.objects.get(pk=request.data["id"])
            l = Like.objects.create(liker=request.user, comment=comment)
            l.save()
            if comment.author != request.user:
                n = Notification.objects.create(
                    notification_type="LIKE",
                    to_user=comment.author,
                    from_user=request.user,
                    post=comment,
                )
                n.save()
        else:
            post = Post.objects.get(pk=request.data["id"])
            l = Like.objects.create(liker=request.user, post=post)
            l.save()
            if post.author != request.user:
                n = Notification.objects.create(
                    notification_type="LIKE",
                    to_user=post.author,
                    from_user=request.user,
                    post=post,
                )
                n.save()

        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        post = Post.objects.get(pk=request.GET.get("post_id"))
        post.like.remove(request.user)

        return Response(status=status.HTTP_202_ACCEPTED)


class LikeCommentView(APIView):
    serializer_class = CommentSerializer

    def post(self, request):
        comment = Comment.objects.get(pk=request.data["comment_id"])
        comment.like.add(request.user)
        n = Notification.objects.create(
            notification_type="LIKE",
            to_user=comment.author,
            from_user=request.user,
            comment=comment,
        )
        n.save()

        return Response(status=status.HTTP_202_ACCEPTED)

    def delete(self, request):
        comment = Comment.objects.get(pk=request.GET.get("comment_id"))
        comment.like.remove(request.user)

        return Response(status=status.HTTP_202_ACCEPTED)


class CommentView(APIView):
    serializer_class = CommentSerializer

    def get(self, request):
        try:
            post = Post.objects.get(pk=request.query_params.get("id"))
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)

            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, formate=None):
        post = Post.objects.get(pk=request.data["post"])
        comment = Comment.objects.create(
            author=request.user, post=post, body=request.data["body"]
        )
        comment.save()
        n = Notification.objects.create(
            notification_type="COMMENT",
            to_user=comment.author,
            from_user=request.user,
            comment=comment,
        )
        n.save()
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        try:
            comment = Comment.objects.get(
                author=request.user, pk=request.query_params.get("id")
            )
            comment.delete()

            return Response(status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ThreadsView(APIView):
    serializer_class = ThreadsSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
        thread1 = Thread.objects.filter(user=request.user)
        thread2 = Thread.objects.filter(receiver=request.user)
        thread = thread1 | thread2
        serializer = ThreadsSerializer(thread, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ThreadView(APIView):
    serializer_class = ThreadSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
        thread = Thread.objects.get(pk=request.query_params.get("thread_id"))
        serializer = ThreadSerializer(thread, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if request.method["isImage"] == True:
            thread = Thread.objects.create(image=request.FILES["image"])
        elif request.method["isImage"] == False:
            thread = Thread.objects.create(image=request.data["message"])
        post = Post.objects.create(author=request.user, body=request.data["body"])
        post.save()
        if request.FILES.getlist("media"):
            for media in request.FILES.getlist("media"):
                print(media)
                post_meida = PostMedia.objects.create(
                    post=post, media=media, media_type="image"
                )
                post_meida.save()


class MessageView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        if Thread.objects.get(
            user=request.user, receiver=request.data["receiver"]
        ) or Thread.objects.get(user=request.data["receiver"], receiver=request.user):

            if request.data["isImage"] == True:
                thread = Thread.objects.create(image=request.FILES["image"])
            if request.method["isImage"] == False:
                thread = Thread.objects.create(image=request.data["message"])

    def put(self, request):
        print(request.data["msg_id"])
        Message.objects.filter(pk=request.data["msg_id"]).update(is_read=True)

        return Response(status=status.HTTP_200_OK)


class NotificationsView(APIView):
    serializer_class = NotificationSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user.notification_to.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        print(request.data)
        Notification.objects.filter(pk=request.data["n_id"]).update(user_has_seen=True)
        return Response(status=status.HTTP_200_OK)


class PostsView(APIView):
    serializer_class = PostSerializer

    def get(self, request):
        if request.query_params.get("liked_id"):
            user = User.objects.get(pk=request.query_params.get("liked_id"))
            posts = Post.objects.filter(likes__liker=user).order_by("-likes__created")
        if request.query_params.get("user_id"):
            user = User.objects.get(pk=request.query_params.get("user_id"))
            posts = Post.objects.filter(author=user).order_by("-created")

        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data)


class SearchView(APIView):
    def get(self, request):
        search = request.query_params.get("search")
        if request.query_params.get("isPost") == "1":
            posts = Post.objects.all()
            posts = posts.filter(Q(body__icontains=search))
            posts = sorted(
                posts, key=lambda post: -(post.likes.count() + post.comments.count())
            )

            serializer = PostSerializer(posts, many=True)

            return Response(serializer.data)

        elif request.query_params.get("isPost") == "0":
            users = User.objects.all()

            users = users.filter(
                Q(username__icontains=search) | Q(profile__bio__icontains=search)
            ).exclude(pk=self.request.user.pk)
            common_connections = (
                request.user.followers.all() & request.user.following.all()
            )
            users = sorted(
                users,
                key=lambda user: -(
                    user.followers.filter(id__in=common_connections).count()
                    + user.following.filter(id__in=common_connections).count()
                ),
            )

            serializer = UserSerializer(users, many=True)

            return Response(serializer.data)

        return Response(status=status.HTTP_404_NOT_FOUND)
