
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
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
