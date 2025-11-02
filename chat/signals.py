# # chat/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Notification
# from .utils import push_notification

# @receiver(post_save, sender=Notification)
# def notification_created(sender, instance, created, **kwargs):
#     """
#     Signal triggered when a Notification is created.
#     Pushes the notification in real-time to the recipient.
#     """
#     if created:
#         push_notification(instance)


# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Message, Notification, NotificationType
# from .utils import push_notification

# @receiver(post_save, sender=Message)
# def message_notification(sender, instance, created, **kwargs):
#     """
#     Trigger a notification when a new message is created.
#     """
#     if created:
#         Notification.objects.create(
#             recipient=instance.match.get_other_user(instance.sender),
#             actor=instance.sender,
#             notification_type=NotificationType.MESSAGE,
#             object_id=instance.id,
#             content=f"{instance.sender.first_name} sent you a message"
#         )

