# match/models.py

from django.db import models
from django.conf import settings

# Create your models here.
class ACTION(models.TextChoices):
    LIKE = 'like', 'like'
    SUPERLIKE = 'superlike', 'superlike'
    IGNORE = 'ignore', 'ignore'

class Swipe(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='swipes_recieved', on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Matches: {self.user1} with {self.user2} and Match_id:{self.id}"

