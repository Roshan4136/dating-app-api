from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import (
    status, generics
)
from django.core.cache import cache
import random
from .serializers import (
    EmailSerializer, VerifyEmailSerializer,
    PhoneSerializer, VerifyOtpSerializer,
    ProfileSerializer, MyUserSerializer,
    LoginUserSerializer, VerifyUserSerializer,
    TimelineSerializer, OppUserDetailSerializer,
    ChangePasswordSerializer, HobbySerializer,
)
from .models import (
    MyUser, Profile, LifestyleChoice, Hobby,
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404
import re
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import F, FloatField, ExpressionWrapper, Func, IntegerField, Q
from django.db.models.functions import Now, ExtractYear
from math import pi, radians
from rest_framework import serializers
from match.models import Block
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

def get_access_token(user):
    token = AccessToken.for_user(user)
    return str(token)

# ...existing code...
class EmailAPIView(APIView):
    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            if MyUser.objects.filter(email=email).exists():
                return Response(
                    {
                        "message": "This email exists."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            otp_for_email = random.randint(100000, 999999)

            # store raw password temporarily (short timeout) so create_user can hash it correctly
            cache.set(email, {"otp_for_email": otp_for_email, "password": password}, timeout=300)
            send_mail(
                subject="Your Verification code for signup.",
                message=f"your OTP Code is {otp_for_email}. It will expire in 3 minutes",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
                
            )
            
            return Response(
                {
                    "message": "OTP sent successfully",
                    "email": email
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": "serializer is not valid."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
# class ResendOtpAPIView(APIView):
#     def post(self, request):
#         serializer = EmailSerializer(data=request.data)
#         if serializer.is_valid():
#             email = serializer.validated_data['email']

#             cached_data = cache.get(email)
#             if cached_data is None:
#                 return Response(
#                     {
#                         "error": "No pending verification found for this email."
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             otp_for_email = random.randint(100000, 999999)
#             cached_data["otp_for_email"] = otp_for_email
#             cache.set(email, cached_data, timeout=300)

#             send_mail(
#                 subject="Your Verification code for signup.",
#                 message=f"your OTP Code is {otp_for_email}. It will expire in 3 minutes",
#                 from_email=settings.EMAIL_HOST_USER,
#                 recipient_list=[email],
#                 fail_silently=False
                
#             )
            
#             return Response(
#                 {
#                     "message": "OTP resent successfully",
#                     "email": email
#                 },
#                 status=status.HTTP_200_OK
#             )
#         return Response(
#             {
#                 "error": "serializer is not valid."
#             },
#             status=status.HTTP_400_BAD_REQUEST
#         )

# ...existing code...
class VerifyEmailAPIView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "serializer is not valid."}, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        user_otp = serializer.validated_data["otp"]

        # check existing user
        if MyUser.objects.filter(email=email).exists():
            return Response(
                {"message": "account with this email address already exists. please login"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # check cache for otp
        cached_data = cache.get(email)
        if cached_data is None:
            return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

        # verify otp
        if str(cached_data["otp_for_email"]) != str(user_otp):
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


        # create user using the raw password (Django will hash it)
        raw_password = cached_data["password"]
        user = MyUser.objects.create_user(
            email=email,
            password=raw_password,
            # is_verified=True,
        )

        # cleanup cache
        cache.delete(email)

        # authenticate user with raw password
        user = authenticate(request, email=email, password=raw_password)

        
        if not user:
            return Response({"message": "something went wrong."}, status=status.HTTP_401_UNAUTHORIZED)

        # success
        access_token = get_access_token(user)
        return Response(
            {
                "message": "verification successful. Proceed to profile setup.",
                "email": email,
                "token": access_token,
            },
            status=status.HTTP_200_OK,
        )
# ...existing code...

# not in use
class VerifyPhoneAPIView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_no']

            if MyUser.objects.filter(phone_no=phone).exists():
                return Response(
                    {
                        "message": "This number is already Verified."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            otp = random.randint(100000, 999999)

            cache.set(phone, otp, timeout=300)

            # SMS sending via twilio
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # client.messages.create(
            #     body=f"Your OTP is {otp}. It will expire in 5 minutes.",
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=phone
            # )

            print(f"OTP for {phone}: {otp}") # for testing only

            return Response(
                {
                    "message": "OTP sent successfully",
                    "phone": phone
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "error": "serializer is not valid."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

# not in use        
class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_no']
            user_otp = serializer.validated_data['otp']

            if MyUser.objects.filter(phone_no=phone).exists():
                return Response({'message':'account with this phone number already exists. please login'}, status=status.HTTP_403_FORBIDDEN)

            cached_otp = cache.get(phone)
            if cached_otp is None:
                return Response(
                    {
                        "error": "OTP expired or not found."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if cached_otp == user_otp:
                cache.delete(phone)
                # cache.set(f"{phone}_verified", True, timeout=6000)
                MyUser.objects.create(phone_no=phone)
                return Response(
                    {
                        "message": "OTP verified. Proceed to profile setup.",
                        "phone": phone
                    },
                    status=status.HTTP_200_OK
                )
            return Response({"error":"Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "serializer is not valid."}, status=status.HTTP_400_BAD_REQUEST)

# not in use
class RegisterUserAPIView(APIView):
    def post(self, request):
        phone = request.data.get('phone_no')
        
        user = get_object_or_404(MyUser, phone_no=phone)
        
        if user.email not in (None, ""):
            raise serializers.ValidationError("User with this phone number already registered, please login. ")
   
        print(request.data)
        serializer = MyUserSerializer(data=request.data, context={'request':request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User Registered Successfully."
                },
                status=status.HTTP_201_CREATED
            )
        print(serializer.errors)
        return Response({"message": "serializer error"}, status=status.HTTP_400_BAD_REQUEST)

class LoginUserAPIView(APIView):
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        # Authenticate directly (avoid MyUser.objects.get which raises DoesNotExist)
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"message": "email or password wrong"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if hasattr(user, 'profile'):
            has_profile = True
        else:
            has_profile = False

        access_token = get_access_token(user)
        return Response(
            {
                "message": "verification successful.",
                "email": email,
                "has_profile": has_profile,
                "token": access_token
            },
            status=status.HTTP_200_OK
        )

def parse_formdata_to_json(formdata):
    data = {}
    images_list = []
    list_fields = {}

    for key, value in formdata.items():
        # Handle images_data separately
        if key.startswith('images_data['):
            images_list.append({'photo': value})
            continue

        # Match nested list with dict keys: e.g. social_links[0][link_url]
        m = re.match(r'(\w+)\[(\d+)\]\[(\w+)\]', key)
        if m:
            field, index, subfield = m.groups()
            index = int(index)
            if field not in list_fields:
                list_fields[field] = []
            while len(list_fields[field]) <= index:
                list_fields[field].append({})
            list_fields[field][index][subfield] = value
            continue

        # Match simple lists: e.g. interests[0]
        m = re.match(r'(\w+)\[(\d+)\]', key)
        if m:
            field, index = m.groups()
            index = int(index)
            if field not in list_fields:
                list_fields[field] = []
            while len(list_fields[field]) <= index:
                list_fields[field].append(None)
            list_fields[field][index] = value
            continue
        
        # ✅ NEW: handle nested dict without index
        m = re.match(r'(\w+)\[(\w+)\]', key)
        if m:
            field, subfield = m.groups()
            if field not in data:
                data[field] = {}
            data[field][subfield] = value
            continue

        # Normal field
        data[key] = value

    if images_list:
        data['images_data'] = images_list
    data.update(list_fields)

    return data

class HobbyListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hobbies = Hobby.objects.all()
        serializer = HobbySerializer(hobbies, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class SetupProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        print(request.data)
        json_data = parse_formdata_to_json(request.data)
        # print(f"after parsing:    {json_data}")
        serializer = ProfileSerializer(data=json_data, context={'request':request})
        if serializer.is_valid():
            print(f"validated data: {serializer.validated_data}")
            profile = serializer.save(user=request.user) 
            response_serializer = ProfileSerializer(profile, context={'request': request})
            return Response(
                {
                    "message": "profile setup completed. ",
                    "data" : response_serializer.data
                },
                status=status.HTTP_200_OK
            )  
        print(f"serializer errors: {serializer.errors}") 
        return Response(
            {
                "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class VerifyUserAPIView(APIView):
    def post(self, request):
        serializer = VerifyUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        otp = serializer.validated_data.get("otp")
        cached_otp = cache.get(email)
        if int(cached_otp) is not None and int(cached_otp) == int(otp):
            cache.delete(email)
            user = get_object_or_404(MyUser, email=email)
            user.is_verified = True
            user.save()
            access_token = get_access_token(user)
            return Response(
                {
                    "message": "verification successfull",
                    "email": email,
                    "token": access_token
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "message": "incorrect or invalid otp"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class DetailUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return Response(
                {
                    "error": "Profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProfileSerializer(profile, context={'request':request})
        # print(f"serialized data: {serializer.data}")
        return Response(
            {
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )

class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile = request.user.profile
        json_data = parse_formdata_to_json(request.data)
        json_data = json_data.get('profile', json_data)

        serializer = ProfileSerializer(instance=profile, data=json_data, partial=True, context={'request':request})
        serializer.is_valid(raise_exception=True)
        # print(f"Data after validation : {serializer.validated_data}")
        serializer.save(profile=profile)
        return Response(
            {
                "message": "successfully updated.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class DeleteSocialAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, social_id):
        profile = request.user.profile
        social_account = profile.social_links.filter(id=social_id).first()
        if social_account is not None:
            social_account.delete()
            return Response(
                {
                    "message": "social account deleted successfully."
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "message": "social account not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
class DeleteImageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, image_id):
        profile = request.user.profile
        image = profile.images.filter(id=image_id).first()
        if image is not None:
            image.delete()
            return Response(
                {
                    "message": "image deleted successfully."
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "message": "image not found."
            },
            status=status.HTTP_404_NOT_FOUND
        )
        
class TimelineAPIView(generics.ListAPIView):
    serializer_class = TimelineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Only real model fields can go here
    filterset_fields = ['gender', 'intention', 'dob']

    # Searchable fields
    search_fields = ['first_name', 'bio']

    # Fields allowed for ordering (annotated fields can be used if present in queryset)
    ordering_fields = ['dob', 'distance', 'age']

    def get_queryset(self):
        user_profile = self.request.user.profile

        # blocked_users = Block.objects.filter(blocker=self.request.user).values_list('blocked', flat=True)
        blocked_users = Block.objects.filter(
            Q(blocker=self.request.user) | Q(blocked=self.request.user)
        ).values_list('blocked', 'blocker')

        # flatten into list of ids
        blocked_ids = [uid for pair in blocked_users for uid in pair]

        qs = Profile.objects.exclude(user=self.request.user).exclude(user__in=blocked_ids)

        # # Base queryset
        # qs = Profile.objects.exclude(user=self.request.user).exclude(user__in=blocked_users)

        # Annotate age and distance only if user has location
        if user_profile.latitude is not None and user_profile.longitude is not None:
            user_lat = radians(user_profile.latitude)
            user_lon = radians(user_profile.longitude)
            R = 6371  # Earth radius in km

            qs = qs.annotate(
                # Distance calculation using spherical law of cosines
                distance=ExpressionWrapper(
                    R * Func(
                        Func(
                            Func(F('latitude')*pi/180, function='COS') *
                            Func(user_lat, function='COS') *
                            Func(F('longitude')*pi/180 - user_lon, function='COS') +
                            Func(F('latitude')*pi/180, function='SIN') *
                            Func(user_lat, function='SIN'),
                            function='ACOS'
                        ),
                        function='ABS'
                    ),
                    output_field=FloatField()
                )
            )

        # Annotate age (approximate, for filtering/order)
        qs = qs.annotate(
            age_annotated=ExpressionWrapper(
                ExtractYear(Now()) - ExtractYear(F('dob')),
                output_field=IntegerField()
            )
        )

        # Manually filter annotated fields from query params
        distance_lte = self.request.query_params.get('distance__lte')
        if distance_lte is not None and 'distance' in qs.query.annotations:
            qs = qs.filter(distance__lte=float(distance_lte))

        age_annotated_gte = self.request.query_params.get('age__gte')
        if age_annotated_gte is not None and 'age_annotated' in qs.query.annotations:
            qs = qs.filter(age_annotated__gte=int(age_annotated_gte))

        return qs

class OppUserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):  
        profile = get_object_or_404(Profile, id=pk)
        # if request.user in profile.blocked_by.all():
        #     return Response({"detail": "You cannot view this profile."}, status=403)

        serializer = OppUserDetailSerializer(profile, context={'request':request})
        return Response(
            {
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
 
class ChangePasswordAPIView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not MyUser.objects.filter(email=email).exists():
            return Response({"message": "No account associated with this email."}, status=status.HTTP_404_NOT_FOUND)

        otp_for_email = random.randint(100000, 999999)
        cache.set(email, otp_for_email, timeout=300)

        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP Code is {otp_for_email}. It will expire in 3 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        return Response(
            {
                "message": "OTP sent successfully",
                "email": email
            },
            status=status.HTTP_200_OK
        )
    
class ForgotPasswordVerifyAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user_otp = request.data.get('otp')

        cached_otp = cache.get(email)
        if cached_otp is None:
            return Response({"error": "OTP expired or not found."}, status=status.HTTP_400_BAD_REQUEST)

        if str(cached_otp) != str(user_otp):
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        cache.delete(email)

        return Response({"message": "Password reset successful.", "email": email}, status=status.HTTP_200_OK)
    
class FotgotPasswordConfirmAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(MyUser, email=email)
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
    

# def parse_formdata_to_json(formdata):
#     data = {}
#     images_list = []

#     for key, value in formdata.items():
#         if key.startswith('images_data['):
#             images_list.append({'photo': value})
#         else:
#             data[key] = value

#     if images_list:
#         data['images_data'] = images_list

#     return data

# def parse_formdata_to_json(formdata):
#     """
#     Convert flat form-data (with bracket notation) into nested dict/list.
#     e.g. profile[images_data][0][photo] -> {"profile": {"images_data": [{"photo": value}]}}
#     Works with both text fields and files (InMemoryUploadedFile).
#     """
#     data = {}

#     for key, value in formdata.items():
#         parts = re.findall(r'\w+', key)  # split by brackets
#         ref = data

#         for i, part in enumerate(parts):
#             last = (i == len(parts) - 1)
#             if part.isdigit():
#                 part = int(part)

#             if last:
#                 # Assign value
#                 if isinstance(ref, list):
#                     while len(ref) <= part:
#                         ref.append(None)
#                     ref[part] = value
#                 else:
#                     ref[part] = value
#             else:
#                 next_part = parts[i + 1]
#                 is_next_index = next_part.isdigit()

#                 if isinstance(ref, list):
#                     while len(ref) <= part:
#                         ref.append([] if is_next_index else {})
#                     ref = ref[part]
#                 else:
#                     if part not in ref:
#                         ref[part] = [] if is_next_index else {}
#                     ref = ref[part]

#     return data
