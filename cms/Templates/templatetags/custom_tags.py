from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter(name='is_admin')
def is_admin(user):
    return user.is_admin