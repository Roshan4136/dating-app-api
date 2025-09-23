from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from .models import Swipe, Match, Block
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import MatchSerializer, BlockListSerializer
from user.serializers import TimelineSerializer
from user.models import MyUser
from rest_framework.generics import ListAPIView



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

class BlockAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        blocker = request.user
        blocked_id = request.data.get('blocked_id')   # arko user ko id
        try:
            blocked = MyUser.objects.get(id=blocked_id)
        except MyUser.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        Block.objects.create(
            blocker=blocker,
            blocked=blocked
        )

        return Response(
            {"message": "Successfully blocked the user."},
            status=status.HTTP_201_CREATED
        )
    
class UnblockAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, block_id):
        blocker = request.user
        block_obj = get_object_or_404(Block, id=block_id, blocker=blocker)

        block_obj.delete()

        return Response(
            {"message": "Successfully unblocked the user."},
            status=status.HTTP_200_OK
        )

class BlockListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BlockListSerializer

    def get_queryset(self):
        return Block.objects.filter(blocker=self.request.user)
    
# class BlockListAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         blocker = request.user
#         block_list = Block.objects.filter(blocker=blocker)
#         serializer = BlockListSerializer(block_list, many=True)
#         return Response(
#             {
#                 "message": "successfully fetched the list.",
#                 "data": serializer.data
#             },
#             status=status.HTTP_200_OK
#         )
        

