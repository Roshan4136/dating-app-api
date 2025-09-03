from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import (
    status, generics
)
from django.core.cache import cache
import random
from .serializers import (
    PhoneSerializer, VerifyOtpSerializer,
    ProfileSerializer, MyUserSerializer,
    LoginUserSerializer, VerifyUserSerializer,
    TimelineSerializer,
)
from .models import (
    MyUser, Profile,
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
from django.db.models import F, FloatField, ExpressionWrapper, Func, IntegerField
from django.db.models.functions import Now, ExtractYear
from math import pi, radians


class VerifyPhoneAPIView(APIView):
    def post(self, request):
        serializer = PhoneSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_no']

            if MyUser.objects.filter(phone_no=phone).exists():
                return Response(
                    {
                        "message": "This number already have an account. Please Login."
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
                cache.set(f"{phone}_verified", True, timeout=6000)
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

class RegisterUserAPIView(APIView):
    def post(self, request):
        phone = request.data.get('phone_no')
        if not MyUser.objects.filter(phone_no=phone).exists():
            return Response(
                {
                    "message": "Verify your phone number first "
                }
            )
        # if not cache.get(f"{phone}_verified"):
        #     return Response({"error": "Phone not verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = MyUserSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "User Registered Successfully."
                },
                status=status.HTTP_201_CREATED
            )
        cache.delete(f"{phone}_verified")
        return Response({"message": "serializer error"}, status=status.HTTP_400_BAD_REQUEST)

def get_access_token(user):
    token = AccessToken.for_user(user)
    return str(token)

class LoginUserAPIView(APIView):
    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {
                    "message": "No User found."
                },
                status=status.HTTP_404_NOT_FOUND
            )
        if user and user.is_verified:
            access_token = get_access_token(user)
            return Response(
                {
                    "message": "verification successfull.",
                    "email": email,
                    "token": access_token
                },
                status=status.HTTP_200_OK
            )
        if user and not user.is_verified:
            otp_code = random.randint(100000, 999999)
            cache.set(email, otp_code, timeout=1800)
            send_mail(
                subject="Your Verification code for Login.",
                message=f"your OTP Code is {otp_code}. It will expire in 3 minutes",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
                
            )
            return Response(
                {
                    "message": "verification otp send to your email",
                    "email": email
                },
                status=status.HTTP_200_OK
            )

def parse_formdata_to_json(formdata):
    """
    Convert flat form-data with bracket notation into nested dict/list:
    - images_data[0], images_data[1] -> [{'photo': ...}, ...]
    - interests[0], interests[1] -> ['interest1', 'interest2', ...]
    - other fields remain as-is
    """
    data = {}
    images_list = []
    list_fields = {}  # for interests or other bracketed lists

    for key, value in formdata.items():
        # Handle images_data separately
        if key.startswith('images_data['):
            images_list.append({'photo': value})
            continue

        # Handle bracketed list fields like interests[0], interests[1]
        m = re.match(r'(\w+)\[(\d+)\]', key)
        if m:
            field, index = m.groups()
            index = int(index)
            if field not in list_fields:
                list_fields[field] = []
            while len(list_fields[field]) <= index:
                list_fields[field].append(None)
            list_fields[field][index] = value
        else:
            # Normal field
            data[key] = value

    # Merge lists into data
    if images_list:
        data['images_data'] = images_list
    data.update(list_fields)

    return data

class SetupProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        print(request.data)
        json_data = parse_formdata_to_json(request.data)
        serializer = ProfileSerializer(data=json_data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)    
        return Response(
            {
                "message": "profile setup completed. ",
                "data" : serializer.data
            },
            status=status.HTTP_200_OK
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
        user = request.user
        serializer = ProfileSerializer(user, context={'request':request})

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

        serializer = ProfileSerializer(data=json_data, instance=profile, partial=True, context={'request':request})
        serializer.is_valid(raise_exception=True)
        print(f"Data after validation : {serializer.validated_data}")
        serializer.save(profile=profile)
        return Response(
            {
                "message": "successfully updated.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
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

        # Base queryset
        qs = Profile.objects.exclude(user=self.request.user)

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
