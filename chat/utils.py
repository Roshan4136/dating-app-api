# # chat/utils.py (new helper function)
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

# def push_notification(notification):
#     """
#     Sends a notification in real-time to the recipient via Channels.
#     Uses the 'user_<id>' group for each recipient.
#     """
#     channel_layer = get_channel_layer()
#     group_name = f"user_{notification.recipient.id}"

#     # Send event to the channel layer; triggers send_notification in consumer
#     async_to_sync(channel_layer.group_send)(
#         group_name,
#         {
#             "type": "send_notification",  # matches method name in consumer
#             "notification_type": notification.notification_type,
#             "content": notification.content,
#             "object_id": notification.object_id,
#         }
#     )
