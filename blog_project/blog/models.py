
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
class BlogUserManager(BaseUserManager):
    def get_queryset(self):
        # Exclude soft-deleted users
        return super().get_queryset().filter(is_deleted=False)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class BlogUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete field
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = BlogUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()





class PasswordResetRequest(models.Model):
    user = models.ForeignKey('BlogUser', on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)  # OTP field
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when OTP is created

    def is_expired(self):
        # Check if OTP is older than 10 minutes
        expiration_time = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiration_time



class EmailVerification(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        expiration_time = self.created_at + timezone.timedelta(hours=24)
        return timezone.now() > expiration_time


class Blog(models.Model):
    PUBLIC='public'
    PRIVATE='private'
    VISIBILITY_CHOICES=[
        (PUBLIC,'public'),
        (PRIVATE,'private'),
    ]
    title = models.CharField(max_length=255,unique=True)
    content = models.TextField()
    author = models.ForeignKey(BlogUser, on_delete=models.CASCADE, related_name='blogs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private=models.CharField(max_length=7,choices=VISIBILITY_CHOICES,default=PUBLIC)
    image=models.ImageField(upload_to='images',null=True,blank=True)
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(BlogUser, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.email} on {self.blog.title}"
