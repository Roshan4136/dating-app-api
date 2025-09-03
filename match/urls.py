from django.urls import path
from .views import (
    SwipeAPIView, MatchAPIView,
)

urlpatterns = [
    path('', SwipeAPIView.as_view(), name='swipe'),
    path('matches/', MatchAPIView.as_view(), name='match'),

]
