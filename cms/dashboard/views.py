
from django.shortcuts import render, redirect
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from . models import Blog, Comment, User
from . serializer import BlogSerializer, CommentSerializer, UserSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db.models import F, Value
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
import json
from . decorator import is_admin
from . forms import SignupForm
from django.contrib.auth import logout

# token authentication 
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_admin'] = user.is_admin
        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# user signup 
def signup(request):
    form = SignupForm()
    context = {}
    message = None
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.is_active = True
            obj.save()
            context['message'] = 'Signup Success!'
            context['res_status'] = status.HTTP_201_CREATED
        else:
            context['res_status'] = status.HTTP_202_ACCEPTED
            context['message'] = 'Something went wrong'
            print(form.errors, 'error')
        return JsonResponse({'data':context})
    context['form'] = form
    return render(request, 'signup.html', context=context)
# logout 
@csrf_exempt
def Logout(request):
    logout(request)
    return JsonResponse({'message':'Logout Success'})

# home page with all blogs
@csrf_exempt
def home(request):
    blogs = Blog.objects.all()
    context = {
        'blogs': blogs
    }
    return render(request, 'home.html', context=context)

# user login page
def user_login(request):
    return render(request, 'login.html')


def create_blog(request):
    return render(request, 'create_blog.html')

# for create a new blog
class Blogs(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        title = data.get('title')
        description = data.get('description')
        try:
            image = request.FILES['image']
        except:
            image = None
        created_by = request.user
        try:
            if not title or not description or not image or not created_by:
                raise ValueError(
                    "All fields (title, description, image, created_by) are required.")
            Blog.objects.create(
                title=title,
                description=description,
                image=image,
                created_by=created_by,
            )
            message = 'Blog created!'
            res_status = status.HTTP_201_CREATED
        except Exception as e:
            message = 'Something went wrong'
            res_status = status.HTTP_202_ACCEPTED
        context = {'message': message, 'status': res_status}
        return JsonResponse({'data': context})

# view blogs page, user can read blogs and comment on blogs.
class ViewBlog(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, id):
        comment = None
        is_liked = None
        likes = None
        if 'like' in request.POST:
            try:
                blog = Blog.objects.get(id=id)
                is_liked = blog.liked_by.filter(email=request.user.email)
                likes = blog.likes
                if not is_liked:
                    blog.liked_by.add(request.user)
                    blog.likes = F('likes') + Value(1)
                    blog.save()
                    is_liked = True
                else:
                    blog.liked_by.remove(request.user)
                    blog.likes = F('likes') - Value(1)
                    blog.save()
                    is_liked = False
                likes = blog.liked_by.all().count()
            except Exception as e:
                return redirect('home')
        if 'comment' in request.POST:
            comment = request.POST.get('comment')
            blog = None
            try:
                blog = Blog.objects.get(id=id)
                comment = Comment.objects.create(
                    comment=comment,
                    commented_by=request.user,
                    content=blog,
                )
                comment = CommentSerializer(comment, many=False)
            except Exception as e:
                pass
        context = {
            'is_liked': is_liked,
            'comment': comment.data if comment else comment,
            'likes':likes,
        }
        return JsonResponse({'data': context})

    def get(self, request, id):
        try:
            blog = Blog.objects.get(id=id)
        except Exception as e:
            return redirect('home')
        if blog.liked_by.filter(id=request.user.id).exists():
            user_liked = True
        else:
            user_liked = False
        my_object = Blog.objects.get(id=id)
        my_object.views = F('views') + 1
        my_object.save()
        my_object.refresh_from_db()
        views = my_object.views
        comments = Comment.objects.filter(content=blog)
        likes = blog.liked_by.all().count()
        context = {
            'blog': blog,
            'views': views,
            'comments': comments,
            'likes': likes,
            'user_liked' : user_liked,
        }
        return render(request, 'view_blog.html', context=context)

    def delete(self, request, id):
        context = {}
        is_admin = False
        if 'is_admin' in request.data:
            is_admin = True
        context['is_admin'] = is_admin
        try:
            blog = Blog.objects.get(id=id)
            comments = Comment.objects.filter(content=blog)
            comments.delete()
            blog.delete()
            message = 'Blog deleted successfully!'
            context['message'] = message
        except Exception as e:
            context['status'] = status.HTTP_202_ACCEPTED
            return JsonResponse({'data': context})
        context['status'] = status.HTTP_204_NO_CONTENT
        return JsonResponse({'data':context })

# edit blog by admin or the author of the blog
def edit_blog(request, id):
    context = {}
    try:
        blog = Blog.objects.get(id=id)
        context['blog'] = blog
    except Exception as e:
        return redirect('home')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        blog = get_object_or_404(Blog, id=id)

        update_data = {
            'title': title,
            'description': description
        }

        if image:
            update_data['image'] = image

        Blog.objects.filter(id=id).update(**update_data)
        data = {
            'message': 'Blog updated successfully'
        }
        return JsonResponse({'data':data})
    return render(request, 'edit_blog.html', context=context)

# admin page for see all blogs and he can edit or delete blogs
class AdminPanel(APIView):

    def get(self, request):
        blogs = Blog.objects.all()
        context = {
            'blogs':blogs
        }
        return render(request, 'admin/admin_panel.html', context=context)

    def delete(self, request):
        id = request.data.get('id')
        context = {}
        is_admin = False
        if 'is_admin' in request.data:
            is_admin = True
        context['is_admin'] = is_admin
        try:
            blog = Blog.objects.get(id=id)
            comments = Comment.objects.filter(content=blog)
            comments.delete()
            blog.delete()
            message = 'Blog deleted successfully!'
            context['message'] = message
        except Exception as e:
            context['message'] = 'Something went wrong!'
            context['status'] = status.HTTP_202_ACCEPTED
            return JsonResponse({'data': context})
        context['status'] = status.HTTP_204_NO_CONTENT
        return JsonResponse({'data':context })

# All users list, only admin access and change the status of user( block or unblock ) 
class AdminUsers(APIView):

    def get(self, request):
        users = User.objects.all()
        context = {
            'users':users
        }
        return render(request, 'admin/admin_users.html', context=context)

    def post(self, request):
        context = {}
        data = request.data
        id = data.get('id')
        user_status = data.get('status')
        if user_status == 'blocked':
            is_active = True
        elif user_status == 'unblocked':
            is_active = False
        else:
            return redirect('admin_users')
        try:
            user = User.objects.get(id=id)
            user.is_active = is_active
            user.save()
            context['is_active'] = user.is_active
            context['message'] = f'User status Updated for {user.email}!'
            context['status'] = status.HTTP_200_OK
        except Exception as e:
            context['status'] = status.HTTP_202_ACCEPTED
            context['message'] = 'Something went wrong!'
        return JsonResponse({'data':context})

# admin can all blogs comments, and also he can block or approve  comments
class AdminComments(APIView):

    def get(self, request):
        comments = Comment.objects.all()
        context = {
            'comments':comments,
        }
        return render(request, 'admin/admin_comments.html', context=context)
    def post(self, request):
        context = {}
        data = request.data
        id = data.get('id')
        comment_status = data.get('status')
        if comment_status == 'blocked':
            is_active = True
        elif comment_status == 'unblocked':
            is_active = False
        else:
            return redirect('admin_users')
        try:
            comment = Comment.objects.get(id=id)
            comment.is_active = is_active
            comment.save()
            context['is_active'] = comment.is_active
            context['message'] = f'Comment status Updated for {comment.comment}!'
            context['status'] = status.HTTP_200_OK
        except Exception as e:
            context['status'] = status.HTTP_202_ACCEPTED
            context['message'] = 'Something went wrong!'
        return JsonResponse({'data':context})