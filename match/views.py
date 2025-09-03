from django.shortcuts import render
from rest_framework.views import APIView
from .models import Swipe, Match
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import MatchSerializer
from user.serializers import TimelineSerializer


class SwipeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        to_user_id = request.data.get('to_user')
        action_data = request.data.get('action')

        if action_data not in ['like', 'superlike', 'ignore', 'unlike']:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        # handle unlike
        if action_data == 'unlike':
            Swipe.objects.filter(from_user=request.user, to_user_id=to_user_id).delete()
        else:
            Swipe.objects.update_or_create(
                from_user=request.user,
                to_user_id=to_user_id,
                defaults={'action': action_data}
            )

        return Response(
            {"message": "Action recorded successfully."},
            status=status.HTTP_200_OK
        )
    
class MatchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        matches = Match.objects.filter(user1=user) | Match.objects.filter(user2=user)

        if matches.exists():
            match_data = []
            for match in matches:
                other_user = match.user1 if not match.user1==user else match.user2
                serializer = TimelineSerializer(other_user.profile, context={'request':request})
                data = serializer.data

                #optionally including match info too
                data['match_id'] = match.id
                data['matched_at'] = match.created_at
                match_data.append(data)

            return Response(
                {
                    "matches": match_data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message':"No matches found yet."
            },
            status=status.HTTP_200_OK
        )

