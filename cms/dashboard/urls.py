from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    # user side
    path('', views.home, name='home'),
    path('user/login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('user_login/', views.user_login, name='user_login'),
    path('blogs/', views.Blogs.as_view(), name='blogs'),
    path('create/', views.create_blog, name='create'),
    path('view_blog/<int:id>/', views.ViewBlog.as_view(), name='view_blog'),
    path('edit_blog/<int:id>/', views.edit_blog, name='edit_blog'),
    # admin panel
    path('admin_panel/blogs/', views.AdminPanel.as_view(), name='admin_blogs'),
    path('admin_panel/users/', views.AdminUsers.as_view(), name='admin_users'),
    path('admin_panel/comments/', views.AdminComments.as_view(), name='admin_comments'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.Logout, name='logout'),
]
