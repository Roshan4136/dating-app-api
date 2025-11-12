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
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matches_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user1', 'user2')
        # for queries per user + sorting.
        indexes = [
        models.Index(fields=["user1"]),
        models.Index(fields=["user2"]),
        models.Index(fields=["created_at"]),
    ]

    def __str__(self):
        return f"Matches: {self.user1} with {self.user2} and Match_id:{self.id}"
    
class Block(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="blocked_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("blocker", "blocked")
        indexes = [models.Index(fields=["blocker"])]  # to quickly find who a user has blocked.

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked.email}"
    
    

