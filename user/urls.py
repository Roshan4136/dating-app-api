from django.urls import path
from .views import (
    EmailAPIView, VerifyEmailAPIView,
    VerifyPhoneAPIView, VerifyOTPAPIView, RegisterUserAPIView,
    LoginUserAPIView, VerifyUserAPIView, DetailUserAPIView,
    UpdateUserAPIView, SetupProfileAPIView,TimelineAPIView,
    OppUserDetailAPIView, 
)

urlpatterns = [
    # phone number verification
    path('send-otp/', VerifyPhoneAPIView.as_view(), name='send_otp'),
    path('verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp'),

    # Email address verification
    path('send_otp_in_email/', EmailAPIView.as_view(), name='send_otp_in_email'),
    path('verify_otp_of_email/', VerifyEmailAPIView.as_view(), name='veriy_otp_of_email'),
    
    # user registration
    path('register/', RegisterUserAPIView.as_view(), name='registration'),
    path('login/', LoginUserAPIView.as_view(), name='login'),
    path('verify-user-otp/', VerifyUserAPIView.as_view(), name='verify-otp'),
    
    # profile part
    path('profile-detail/', DetailUserAPIView.as_view(), name='detail-user'),
    path('profile-update/', UpdateUserAPIView.as_view(), name='update-profile'),
    path('profile-create/', SetupProfileAPIView.as_view(), name='setup-profile'),

    path('timeline/', TimelineAPIView.as_view(), name='timeline'),
    
    path('detail/<int:pk>/', OppUserDetailAPIView.as_view(), name='opp-user-detail'),
    
]
