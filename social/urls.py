from django.urls import path

from . import views

urlpatterns = [
    path("posts", views.PostsView.as_view()),
    path("like", views.LikeView.as_view()),
    path("comment", views.CommentView.as_view()),
    path("like_comment", views.LikeCommentView.as_view()),
    path("follow/<str:pk>", views.FollowView.as_view()),
    path("message", views.MessageView.as_view()),
    path("allposts", views.all_posts, name="all_posts"),
    path("post/", views.PostView.as_view()),
    path("notifications", views.NotificationsView.as_view(), name="notifications"),
    path("threads", views.ThreadsView.as_view()),
    path("thread", views.ThreadView.as_view()),
    path("search", views.SearchView.as_view()),
]
