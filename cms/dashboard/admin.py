from django.contrib import admin
from . models import User, Blog, Comment
from django.contrib.auth.admin import UserAdmin


# class AccountAdmin(UserAdmin):
#     readonly_fields = ('password',)

admin.site.register(User)
admin.site.register(Blog)
admin.site.register(Comment)
