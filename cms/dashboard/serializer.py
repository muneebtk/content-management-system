from rest_framework import serializers
from . models import Blog, Comment, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
class BlogSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()
    
    class Meta:
        model = Blog
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    # content = BlogSerializer()
    commented_by = UserSerializer()

    class Meta:
        model = Comment
        fields = '__all__'