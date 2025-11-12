from django.urls import path
from .views import (
    EmailAPIView, VerifyEmailAPIView,
    ForgotPasswordAPIView, ForgotPasswordVerifyAPIView, FotgotPasswordConfirmAPIView,
    VerifyPhoneAPIView, VerifyOTPAPIView, RegisterUserAPIView,
    LoginUserAPIView, VerifyUserAPIView, DetailUserAPIView,
    UpdateUserAPIView, SetupProfileAPIView,TimelineAPIView,
    OppUserDetailAPIView, ChangePasswordAPIView, HobbyListAPIView,
    DeleteSocialAccountAPIView, DeleteImageAPIView,
)

urlpatterns = [
    # phone number verification
    path('send-otp/', VerifyPhoneAPIView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp'),

    # Email address verification
    path('send_otp_in_email/', EmailAPIView.as_view(), name='send_otp_in_email'),
    path('verify_otp_of_email/', VerifyEmailAPIView.as_view(), name='veriy_otp_of_email'),
    
    # ForgotPassword
    path('forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('forgot-password-verify/', ForgotPasswordVerifyAPIView.as_view(), name='forgot_password_verify'),
    path('forgot-password-confirm/', FotgotPasswordConfirmAPIView.as_view(), name='forgot_password_confirm'),

    # user registration
    path('register/', RegisterUserAPIView.as_view(), name='registration'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('verify-user-otp/', VerifyUserAPIView.as_view(), name='verify-otp'),
    
    # Hobby part
    path('hobbies/', HobbyListAPIView.as_view(), name='hobbies-list'),
    
    # profile part
    path('profile-detail/', DetailUserAPIView.as_view(), name='detail-user'),
    path('profile-update/', UpdateUserAPIView.as_view(), name='update-profile'),
    path('profile-create/', SetupProfileAPIView.as_view(), name='setup-profile'),
    
    # Delete apis
    path('delete-social-account/<int:social_id>/', DeleteSocialAccountAPIView.as_view(), name='delete-social-account'),
    path('delete-image/<int:image_id>/', DeleteImageAPIView.as_view(), name='delete-image'),

    path('timeline/', TimelineAPIView.as_view(), name='timeline'),
    
    path('detail/<int:pk>/', OppUserDetailAPIView.as_view(), name='opp-user-detail'),

    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    
]
