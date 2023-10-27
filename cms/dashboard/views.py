from rest_framework_jwt.serializers import JSONWebTokenSerializer
from rest_framework_jwt.views import ObtainJSONWebToken
from django.shortcuts import render, redirect
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        # token['is_super_admin'] = user.is_superadmin
        request = None
        if user.is_active is True:
            # return render(request, 'home.html', {'token':token})
            # return redirect(f'/render_template/?token={token}')
            return token
        else:
            return Response('The user is not active')


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomObtainJSONWebToken(ObtainJSONWebToken):
    print('=============================',)
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainJSONWebToken, self).post(
            request, *args, **kwargs)
        print(request.method, 'this is methos')
        if response.status_code == 200:
            # If the authentication is successful, obtain the token and redirect
            token = response.data.get('token')
            print(token, '------------------------------')
            # Redirect to the template view
            # return redirect(f'/render_template/?token={token}')
            return Response({'token':token})
        return response

    def get(self, request):
        print('999999999999999')
        return render(request, 'login.html')


class RenderTemplateView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        # Include any other context data you need for the template
        template_data = {
            'token': token,
            'additional_data': 'your_additional_data',
        }
        return render(request, 'home.html', template_data)


# @api_view(['GET'])
def home(request):
    return render(request, 'home.html')


# @api_view(['POST'])
def user_login(request):
    return render(request, 'login.html')
