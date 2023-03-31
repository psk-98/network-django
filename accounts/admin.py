from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from social.models import Follow

from .models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = [
            "",
        ]


class ProfileInline(admin.TabularInline):
    model = Profile


class FollowersInline(admin.TabularInline):
    model = Follow
    fk_name = "following"
    extra = 1


class FollowingInline(admin.TabularInline):
    model = Follow
    fk_name = "user"
    extra = 1


class UserFormAdmin(admin.ModelAdmin):
    form = UserForm
    inlines = [ProfileInline, FollowersInline, FollowingInline]


admin.site.unregister(User)
admin.site.register(User, UserFormAdmin)
