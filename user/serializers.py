from rest_framework import serializers
from .models import(
    MyUser, Profile, Image, Hobby,
    SocialLink, LifestyleChoice,
)
from django.contrib.auth.hashers import check_password
from math import radians, sin, cos, sqrt, asin


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, required=True)

class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    otp = serializers.IntegerField()
    
class PhoneSerializer(serializers.Serializer):
    phone_no = serializers.CharField(max_length=15)

class VerifyOtpSerializer(serializers.Serializer):
    phone_no = serializers.CharField(max_length=15)
    otp = serializers.IntegerField()

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'photo']

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['id', 'link_url', 'platform']

class HobbySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Hobby
        fields = ['id', 'name', 'predefined',]

class LifestyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifestyleChoice
        fields = ['id', 'drink_choice', 'smoke_choice', 'active_choice', 'diet_choice', 'pet_choice', 'travel_choice']

class ProfileSerializer(serializers.ModelSerializer):
    lifestyle = LifestyleSerializer(required=False)
    lifestyle_info = LifestyleSerializer(source='profiles_with_lifestyle', read_only=True)

    images_data = ImageSerializer(many=True, write_only=True, required=False)
    images_list = ImageSerializer(source='images', many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, write_only=True, required=False)
    social_links_list = SocialLinkSerializer(source='social_links', many=True, read_only=True)
    hobbies = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True  # only for write
    )
    hobbies_list = HobbySerializer(many=True, source='hobbies', read_only=True)  # for read

    class Meta:
        model = Profile
        fields = [
            'id', 'full_name', 'gender', 'interested_in', 'profile_pic', 'dob', 'relationship',
            'sexual_orientation', 'show_orientation', 'bio', 'location', 'images_data',
            'hobbies', 'hobbies_list', 'images_list', 'latitude', 'longitude',
            'zodiac_sign', 'show_zodiac', 'lifestyle', 'social_links', 'social_links_list', 'lifestyle_info',
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        # if Profile.objects.filter(user=user).exists():

        if Profile.objects.filter(user=user).exists():
            raise serializers.ValidationError("Profile already exists for this user.")  
        
        lifestyle_data = validated_data.pop('lifestyle', None)
        images_data = validated_data.pop('images_data', [])
        hobbies_data = validated_data.pop('hobbies', [])
        # lifestyle_data = validated_data.pop('lifestyles',[])
        social_links_data = validated_data.pop('social_links', [])

        profile = Profile.objects.create(**validated_data)

        if lifestyle_data:
            LifestyleChoice.objects.create(profile=profile, **lifestyle_data)

        # images
        for image in images_data:
            Image.objects.create(profile=profile, **image)

        # social links
        for link_url in social_links_data:
            SocialLink.objects.create(profile=profile, **link_url)

        # interests
        hobbies_objs = []
        for name in hobbies_data:
            clean_name = name.strip().lower()
            obj, created = Hobby.objects.get_or_create(name=clean_name, defaults={'predefined': False})
            hobbies_objs.append(obj)
        profile.hobbies.set(hobbies_objs) 
        return profile

    def update(self, instance, validated_data):
        lifestyle_data = validated_data.pop('lifestyle', None)
        images_data = validated_data.pop('images_data', [])
        hobbies_data = validated_data.pop('hobbies', [])
        social_links_data = validated_data.pop('social_links', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create lifestyle
        if lifestyle_data:
            LifestyleChoice.objects.update_or_create(
                profile=instance,
                defaults=lifestyle_data
            )
            
        if images_data:
            # instance.images.all().delete()
            for image in images_data:
                Image.objects.create(profile=instance, **image)

        if social_links_data:

            for link_url in social_links_data:
                SocialLink.objects.update_or_create(
                    profile=instance,
                    link_url=link_url['link_url'],
                    defaults={'platform': link_url.get('platform', '')}     # update platform if exists
                )

        # Update or add images
        # for image in images_data:
        #     image_id = image.get('id', None)
        #     if image_id:
        #         try:
        #             img_obj = instance.images.get(id=image_id)
        #             if 'photo' in image:
        #                 img_obj.photo = image['photo']
        #                 img_obj.save()
        #         except Image.DoesNotExist:
        #             Image.objects.create(profile=instance, **image)
        #     else:
        #         Image.objects.create(profile=instance, **image)

        # Update interests
        if hobbies_data:
            hobbies_objs = []
            for name in hobbies_data:
                obj, _ = Hobby.objects.get_or_create(name=name)
                hobbies_objs.append(obj)
            instance.hobbies.set(hobbies_objs)

        return instance    

class MyUserSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(required=False)
    # email = serializers.EmailField(write_only=True, required=False)
    phone_no = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = MyUser
        fields = ['id', 'email', 'phone_no', 'password']

    def create(self, validated_data):
        # profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password')
        phone_no = validated_data.get('phone_no')
        email = validated_data.get('email')

        if MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email already exists, please login. ")
        try:
            user = MyUser.objects.get(phone_no=phone_no)
        except MyUser.DoesNotExist:
            raise serializers.ValidationError("Phone number not verified or not found. ")
        for attr, value in validated_data.items():
            setattr(user, attr, value)
            
        if password:
            user.set_password(password)
            user.save()

        return user

        # create user instance but don't save yet
        # user = MyUser(**validated_data)
        # user.set_password(password)

        # # validate profile data if exists
        # if profile_data:
        #     profile_serializer = ProfileSerializer(data=profile_data, context={'user': user})
        #     profile_serializer.is_valid(raise_exception=True)

        # # save user only after all validation passes
        # user.save()

        # # save profile if exists
        # if profile_data:
        #     profile_serializer.save()

        # return user

class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

# not in use
class VerifyUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

def calculate_distance(lat1, lng1, lat2, lng2):
    """
    Calculate distance in kilometers between two points using Haversine formula.
    """
    if None in [lat1, lng1, lat2, lng2]:
        return None
    
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lng1, lat1, lng2, lat2])

    # differences
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Earth radius in km
    return round(km, 2)

class TimelineSerializer(serializers.ModelSerializer):
    images_list = ImageSerializer(source='images', many=True, read_only=True)
    hobbies_list = HobbySerializer(many=True, source='hobbies', read_only=True)
    age = serializers.ReadOnlyField()                               # from the model property
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    distance = serializers.SerializerMethodField()


    class Meta:
        model = Profile
        fields = [
            'user_id', 'id', 'full_name', 'profile_pic', 'dob', 
            'bio', 'location', 'distance', 'gender', 'interested_in',
            'hobbies_list', 'images_list','age',
        ]
    
    def get_distance(self, obj):
        request = self.context['request']
        current_user_lat = request.user.profile.latitude
        current_user_long = request.user.profile.longitude

        if not current_user_lat or not current_user_long:
            return None
        return calculate_distance(obj.latitude, obj.longitude, current_user_lat, current_user_long)
        

class OppUserDetailSerializer(serializers.ModelSerializer):
    hobbies_list = HobbySerializer(source='hobbies', many=True, read_only=True)  # for read
    lifestyle = LifestyleSerializer(source='profiles_with_lifestyle', read_only=True)
    # lifestyle_list = LifestyleSerializer(many=True, read_only=True)
    images_list = ImageSerializer(source='images', many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'id', 'full_name', 'gender', 'profile_pic', 'dob', 'interested_in',
            'relationship', 'sexual_orientation', 'show_orientation', 'bio', 'location', 
            'hobbies_list', 'images_list', 'latitude', 'longitude', 'social_links',
            'zodiac_sign', 'show_zodiac', 'lifestyle', 'distance', 
        ]
        read_only_fields = [
            'id', 'full_name', 'gender', 'profile_pic', 'dob', 'interested_in',
            'relationship', 'sexual_orientation', 'show_orientation', 'bio', 'location', 
            'hobbies_list', 'images_list', 'latitude', 'longitude', 'social_links',
            'zodiac_sign', 'show_zodiac', 'lifestyle', 'distance',
        ]

    def get_distance(self, obj):
        request = self.context['request']
        current_user_lat = request.user.profile.latitude
        current_user_long = request.user.profile.longitude

        if not current_user_lat or not current_user_long:
            return None
        return calculate_distance(obj.latitude, obj.longitude, current_user_lat, current_user_long)
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(max_length=100)
    confirm_password = serializers.CharField(max_length=100)

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if not check_password(old_password, user.password):
            raise serializers.ValidationError(
                {
                    "old_password": "Incorrect old password."
                }
            )
        
        if new_password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "passwords do not match."})
        
        if len(new_password) < 6:
            raise serializers.ValidationError({"new_password": "Passwords must be at least 6 characters long. "})
        
        return attrs
    
    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)  # hashes automatically
        user.save()
        return user

