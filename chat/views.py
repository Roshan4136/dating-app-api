from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from match.models import Match
from .cloudinary import upload_file
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from match.models import Match


class MessageListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

        # Ensure requesting user is part of this match
        if request.user not in [match.user1, match.user2]:
            return Response({"error": "Not authorized"}, status=403)

        messages = Message.objects.filter(match=match).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

# File upload api
class UploadMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle media upload + optional text.
        Expects FormData:
        - file: the image/video
        - text: optional message
        - match_id: chat identifier
        """

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)
        
        text = request.data.get("text", "")
        match_id = request.data.get("match_id")

        if not match_id:
            return Response({"error": "match_id is required"}, status=400)
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return Response({"error": "Match not found"}, status=404)

        if request.user not in [match.user1, match.user2]:
            return Response({"error": "Not authorized"}, status=403)

        
        
        # Determine media type from MIME type
        media_type = file.content_type.split("/")[0] # "image" or "video"

        # Upload to cloudinary
        media_url = upload_file(file, resource_type="auto")
        if not media_url:
            return Response({"error": "Upload failed."}, status=500)
        
        # Save message to DB
        message = Message.objects.create(
            sender=request.user,
            match_id=match_id,
            text=text,
            media_url=media_url,
            media_type=media_type,
            is_read=False
        )

        # Broadcast to Websocket group
        channel_layer = get_channel_layer()
        group_name = f"chat_{match_id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "chat_message",
                "message": text,
                "sender_id": request.user.id,
                "media_url": media_url,
                "media_type": media_type,
                "created_at": message.created_at.isoformat()
            }
        )

        return Response({
            "status": "success",
            "message_id": message.id,
            "media_url": media_url,
            "media_type": media_type
        })
        
         