from rest_framework import filters
from django_filters import rest_framework as django_filters
import logging
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from .models import BlogUser,PasswordResetRequest
from .serializers import SignupSerializer, LoginSerializer, ForgotPasswordSerializer,UpdateUserSerializer
import random
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import EmailVerification
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Blog
from .serializers import BlogSerializer
from django.db import IntegrityError
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import Comment
from .serializers import CommentSerializer
from .filters import BlogFilter  
from django_filters.rest_framework import DjangoFilterBackend








logger = logging.getLogger('blog')

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

          
            verification = EmailVerification.objects.create(user=user)
            verification_link = f"https://www.youtube.com/verify-email/{verification.token}/"
            send_mail(
                "Verify Your Email",
                f"Click the link to verify your email: {verification_link}",
                "noreply@blog.com",
                [user.email]
            )
            
            return Response({"message": "User created successfully. A verification email has been sent."})
        return Response(serializer.errors, status=400)





class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful.",
                "user": {
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                }
            })
        return Response(serializer.errors, status=400)






class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = BlogUser.objects.get(email=email)
            except BlogUser.DoesNotExist:
                return Response({"error": "User with this email does not exist"}, status=400)

            
            otp = str(random.randint(100000, 999999))

           
            reset_request, created = PasswordResetRequest.objects.get_or_create(user=user)
            reset_request.otp = otp
            reset_request.save()

            
            send_mail(
                "Password Reset",
                f"Use this OTP to reset your password: {otp}",
                "noreply@blog.com",
                [email],
            )

            return Response({"message": "Password reset email sent."})
        return Response(serializer.errors, status=400)






class ValidateOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not email or not otp or not new_password:
            return Response({"error": "Email, OTP and new password are required"}, status=400)

        try:
            user = BlogUser.objects.get(email=email)
        except BlogUser.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=400)

        try:
            reset_request = PasswordResetRequest.objects.get(user=user, otp=otp)
        except PasswordResetRequest.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        if reset_request.is_expired():
            return Response({"error": "OTP has expired"}, status=400)

        
        user.set_password(new_password)
        user.save()

        
        reset_request.delete()

        return Response({"message": "Password reset successfully"})







class SendVerificationEmail(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            user = BlogUser.objects.get(email=email)
        except BlogUser.DoesNotExist:
            return Response({"error": "User does not exist"}, status=400)

        verification = EmailVerification.objects.create(user=user)

        
        verification_link = f"https://www.youtube.com/verify-email/{verification.token}/"
        send_mail(
            "Verify Your Email",
            f"Click the link to verify your email: {verification_link}",
            "noreply@blog.com",
            [email]
        )

        return Response({"message": "Verification email sent successfully"})






class VerifyEmail(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        verification = get_object_or_404(EmailVerification, token=token)
    

        if verification.is_expired():
            return Response({"error": "Verification token has expired"}, status=400)

        if verification.is_verified:
            return Response({"message": "Email already verified"}, status=200)

        
        verification.user.is_active = True
        verification.user.save()
        verification.is_verified = True
        verification.save()

        return Response({"message": "Email successfully verified"})





class UpdateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateUserSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully", "user": serializer.data})
        return Response(serializer.errors, status=400)





class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_deleted = True
        user.save()
        return Response({"message": "User deleted successfully"})












class CreateBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug("Create blog request received with data: %s", request.data)

        data = request.data.copy()

        if 'image' in request.FILES:
            data['image'] = request.FILES['image']

        if 'is_private' not in data:
            data['is_private'] = Blog.PUBLIC

        serializer = BlogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            logger.info("Blog created successfully by user: %s", request.user.email)
            return Response(
                {
                    "message": "Blog created successfully",
                    "blog": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        
        logger.error("Blog creation failed, errors: %s", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)







logger = logging.getLogger('blog')

class ListBlogView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.debug("List blog request received")

        
        paginator = PageNumberPagination()
        paginator.page_size = 10  

       
        blogs = Blog.objects.all()

        
        filtered_blogs = BlogFilter(request.GET, queryset=blogs).qs

        paginated_blogs = paginator.paginate_queryset(filtered_blogs, request)

        logger.info("Total blogs retrieved: %d", filtered_blogs.count())

        serializer = BlogSerializer(paginated_blogs, many=True)

        
        return paginator.get_paginated_response(serializer.data)






class UpdateBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, blog_id):
        logger.debug("Update blog request received for blog ID: %d", blog_id)

        try:
            blog = Blog.objects.get(id=blog_id, author=request.user)
        except Blog.DoesNotExist:
            logger.error("Blog not found or user is not the author. Blog ID: %d", blog_id)
            return Response({"error": "Blog not found or you are not the author."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info("Blog updated successfully, Blog ID: %d", blog_id)
            return Response({"message": "Blog updated successfully", "blog": serializer.data})
        
        logger.error("Blog update failed for Blog ID: %d, errors: %s", blog_id, serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class DeleteBlogView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, blog_id):
        logger.debug("Delete blog request received for blog ID: %d", blog_id)

        try:
            blog = Blog.objects.get(id=blog_id, author=request.user)
        except Blog.DoesNotExist:
            logger.error("Blog not found or user is not the author. Blog ID: %d", blog_id)
            return Response({"error": "Blog not found or you are not the author."}, status=status.HTTP_404_NOT_FOUND)
        
        blog.delete()
        logger.info("Blog deleted successfully, Blog ID: %d", blog_id)
        return Response({"message": "Blog deleted successfully"}, status=status.HTTP_204_NO_CONTENT)





class CommentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, blog_id):
        blog = get_object_or_404(Blog, id=blog_id)  
        comments = blog.comments.filter(parent=None)  
        serializer = CommentSerializer(comments, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)  





class CreateCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, blog_id):
        blog = get_object_or_404(Blog, id=blog_id)
        data = request.data.copy()
        data['blog'] = blog.id
        parent_id = request.data.get('parent')

        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id, blog=blog)
            data['parent'] = parent_comment.id

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class UpdateCommentView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, author=request.user)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class DeleteCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, author=request.user)
        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

