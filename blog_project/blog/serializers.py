from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import BlogUser
from .models import Blog
from.models import Comment



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = BlogUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        return BlogUser.objects.create_user(**validated_data)




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        return user



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not BlogUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist")
        return value



class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogUser
        fields = ['first_name', 'last_name', 'email']
        read_only_fields = ['email']  




class BlogSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at','is_private','image']
        read_only_fields = ['author', 'created_at', 'updated_at']



class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'blog', 'author', 'content', 'created_at', 'updated_at','parent','replies']
        read_only_fields = ['author', 'created_at', 'updated_at','replies']



    def get_replies(self,obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(),many=True).data
        return[]
    

    