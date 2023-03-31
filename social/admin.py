from django import forms
from django.contrib import admin

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


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = [
            "",
        ]


class PostMediaInline(admin.TabularInline):
    model = PostMedia


class PostLikesInline(admin.TabularInline):
    model = Like


class PostCommentsInline(admin.TabularInline):
    model = Comment


class PostFormAdmin(admin.ModelAdmin):
    form = PostForm
    inlines = [
        PostMediaInline,
        PostLikesInline,
        PostCommentsInline,
    ]


admin.site.register(Post, PostFormAdmin)
admin.site.register(Follow)
admin.site.register(Notification)
admin.site.register(Thread)
admin.site.register(Message)
