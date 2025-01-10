from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import BlogUser, PasswordResetRequest, EmailVerification, Blog
from django.contrib import admin
from django.utils.html import mark_safe
# Register BlogUser model with custom admin options if needed
@admin.register(BlogUser)
class BlogUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'is_deleted')
    list_filter = ('is_active', 'is_staff', 'is_deleted')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

# Register PasswordResetRequest model
@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp', 'created_at')
    search_fields = ('user__email', 'otp')
    list_filter = ('created_at',)
    
# Register EmailVerification model
@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'is_verified')
    search_fields = ('user__email',)
    list_filter = ('is_verified', 'created_at')

# Register Blog model
from django.contrib import admin
from django.utils.html import mark_safe
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'is_private', 'image_preview')
    list_filter = ('is_private', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__email')
    ordering = ('-created_at',)

    # Method to display the image preview in the list display
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')  # Image preview with a 100px width
        return "No Image"
    
    image_preview.short_description = 'Image'  # Custom label for the image column


