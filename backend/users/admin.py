from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for User model.
    """

    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'last_name')
    ordering = ('username',)
    empty_value_display = '-empty-'


class FollowAdmin(admin.ModelAdmin):
    """
    Admin configuration for Follow model.
    """

    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    ordering = ('user',)
    empty_value_display = '-empty-'


admin.site.register(Follow, FollowAdmin)
admin.site.register(User, UserAdmin)
