from django.urls import path
from .views import SignupView, LoginView, ForgotPasswordView,ValidateOtpView
from .views import SendVerificationEmail, VerifyEmail
from django.conf import settings
from django.conf.urls.static import static
from .views import UpdateUserView, DeleteUserView, CreateBlogView, ListBlogView, UpdateBlogView, DeleteBlogView
from .views import CommentListView, CreateCommentView, UpdateCommentView, DeleteCommentView



urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/validate-otp/', ValidateOtpView.as_view(), name='validate-otp'),
    path('send-verification/', SendVerificationEmail.as_view(), name='send-verification'),
    path('verify-email/<uuid:token>/', VerifyEmail.as_view(), name='verify-email'),
    path('update-user/', UpdateUserView.as_view(), name='update-user'),
    path('delete-user/', DeleteUserView.as_view(), name='delete-user'),
    path('blog/', ListBlogView.as_view(), name='list-blogs'),
    path('blog/create/', CreateBlogView.as_view(), name='create-blog'),
    path('blog/<int:blog_id>/update/', UpdateBlogView.as_view(), name='update-blog'),
    path('blog/<int:blog_id>/delete/', DeleteBlogView.as_view(), name='delete-blog'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)





urlpatterns += [
    path('blog/<int:blog_id>/comments/', CommentListView.as_view(), name='list-comments'),
    path('blog/<int:blog_id>/comments/create/', CreateCommentView.as_view(), name='create-comment'),
    path('comments/<int:comment_id>/update/', UpdateCommentView.as_view(), name='update-comment'),
    path('comments/<int:comment_id>/delete/', DeleteCommentView.as_view(), name='delete-comment'),
]
