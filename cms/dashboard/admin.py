from django.contrib import admin
from . models import User
from django.contrib.auth.admin import UserAdmin


# class AccountAdmin(UserAdmin):
#     readonly_fields = ('password',)

admin.site.register(User)
