# chat/models.py
from django.db import models
from django.conf import settings
from match.models import Match


class Message(models.Model):
    match = models.ForeignKey(
        Match, related_name='messages',
        on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='messages_sent',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.text:
            return f"{self.sender} -> Match {self.match.id}: {self.text[:30]}"
        return f"{self.sender} -> Match {self.match.id}: [Image]"
