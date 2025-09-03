from django.urls import path
from .views import MessageListAPIView

urlpatterns = [
    path('messages/<int:match_id>/', MessageListAPIView.as_view(), name='message-list'),
]
