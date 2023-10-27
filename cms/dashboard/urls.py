from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('user/login/', views.MyTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('render_template/', views.RenderTemplateView.as_view(), name='render_template'),
    path('api-token-auth/', views.CustomObtainJSONWebToken.as_view(), name='api_token_auth'),
    path('user_login/', views.user_login, name='user_login'),

]
