from django.shortcuts import redirect
from functools import wraps

def is_admin(view_func):
    @wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        try:
            if not request.user.is_admin:
                return redirect('home')
            return view_func(self, request, *args, **kwargs)
        except:
            return redirect('user_login')
    return wrapper