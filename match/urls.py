from django.urls import path
from .views import (
    SwipeAPIView, MatchAPIView, BlockAPIView, UnblockAPIView,
    BlockListAPIView
)

urlpatterns = [
    
    path('', SwipeAPIView.as_view(), name='swipe'),
    path('matches/', MatchAPIView.as_view(), name='match'),
    path('block/', BlockAPIView.as_view(), name='block-user'),
    path('block-list/', BlockListAPIView.as_view(), name='block-list'),
    path('unblock/<int:block_id>/', UnblockAPIView.as_view(), name='unblock-user'),
    
]
