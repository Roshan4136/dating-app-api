# chat/models.py
from django.db import models
from django.conf import settings
from match.models import Match

class MediaType(models.TextChoices):
    IMAGE = 'image', 'image'
    VIDEO = 'video', 'video'

class Message(models.Model):
    match = models.ForeignKey(
        Match, related_name='messages',
        on_delete=models.CASCADE              # delete message object if the match object is deleted
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='messages_sent',
        on_delete=models.SET_NULL, null=True, blank=True        # keeps message even if sender deletes account
    )
    text = models.TextField(blank=True, null=True)
    media_url = models.URLField(blank=True, null=True)
    media_type = models.CharField(max_length=7, choices=MediaType.choices, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["match", "created_at"]),   # fast chat retrieval.
        ]

    def __str__(self):
        if self.text:
            return f"{self.sender} -> Match {self.match.id}: {self.text[:30]}"
        return f"{self.sender} -> Match {self.match.id}: [Image]"

# notifications
class NotificationType(models.TextChoices):
    MATCH = "match", "match"
    MESSAGE = "message", "message"
    LIKE = "like", "like"
    SUPERLIKE = "superlike", "superlike"
    SYSTEM = "system", "system"

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name="sent_notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    object_id = models.PositiveIntegerField(null=True, blank=True)          # reference to the Match/Message/etc.
    content = models.TextField(blank=True)      # optional text
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient} - {self.notification_type}"


