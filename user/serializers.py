from rest_framework import serializers
from .models import(
    MyUser, Profile, Image, Interest, LifestyleChoice,
    SocialLink,
)

class PhoneSerializer(serializers.Serializer):
    phone_no = serializers.CharField(max_length=15)
    # email
    
    # def validate_phone_no(self, value):
    #     if not value.startswith("+"):
    #         raise serializers.ValidationError("Phone number must be in E.164 format (+97798xxxxxxxx).")
    #     return value

class VerifyOtpSerializer(serializers.Serializer):
    phone_no = serializers.CharField(max_length=15)
    otp = serializers.IntegerField()

# class ResendOTPSerializer(serializers.Serializer):
#     phone_no = serializers.CharField()

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'photo']

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['id', 'link_url']

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class LifestyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifestyleChoice
        fields = ['id', 'name']

class ProfileSerializer(serializers.ModelSerializer):
    images_data = ImageSerializer(many=True, write_only=True, required=False)
    images_list = ImageSerializer(source='images', many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, write_only=True, required=False)
    social_links_list = SocialLinkSerializer(source='social_links', many=True, read_only=True)
    interests = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True  # only for write
    )
    interests_list = InterestSerializer(many=True, source='interests', read_only=True)  # for read
    lifestyles = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        write_only=True  # only for write
    )
    lifestyle_list = LifestyleSerializer(many=True, source='lifestyle_choices', read_only=True)
    

    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'gender', 'last_name', 'profile_pic', 'dob', 'looking_for',
            'intention', 'sexual_orientation', 'show_orientation', 'bio', 'location', 'images_data',
            'interests', 'interests_list', 'images_list', 'latitude', 'longitude',
            'zodiac_sign', 'show_zodiac', 'lifestyles', 'lifestyle_list', 'social_links', 'social_links_list',
        ]

    def create(self, validated_data):
        images_data = validated_data.pop('images_data', [])
        interests_data = validated_data.pop('interests', [])
        lifestyle_data = validated_data.pop('lifestyles',[])
        social_links_data = validated_data.pop('social_links', [])

        profile = Profile.objects.create(**validated_data)

        # images
        for image in images_data:
            Image.objects.create(profile=profile, **image)

        # social links
        for link_url in social_links_data:
            SocialLink.objects.create(profile=profile, **link_url)

        # interests
        interest_objs = []
        for name in interests_data:
            obj, _ = Interest.objects.get_or_create(name=name)
            interest_objs.append(obj)
        profile.interests.set(interest_objs) 
    
        # lifestyle choices
        lifestyle_objs = []
        for name in lifestyle_data:
            obj, _ = LifestyleChoice.objects.get_or_create(name=name)
            lifestyle_objs.append(obj)
        profile.lifestyle_choices.set(lifestyle_objs)

        return profile

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images_data', [])
        interests_data = validated_data.pop('interests', [])
        lifestyles_data = validated_data.pop('lifestyles', [])
        social_links_data = validated_data.pop('social_links', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if images_data:
            # instance.images.all().delete()
            for image in images_data:
                Image.objects.create(profile=instance, **image)

        if social_links_data:
            for link_url in social_links_data:
                SocialLink.objects.create(profile=instance, **link_url)

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
        if interests_data:
            interest_objs = []
            for name in interests_data:
                obj, _ = Interest.objects.get_or_create(name=name)
                interest_objs.append(obj)
            instance.interests.set(interest_objs)

        # Update lifestyles
        if lifestyles_data:
            lifestyle_objs = []
            for name in lifestyles_data:
                obj, _ = LifestyleChoice.objects.get_or_create(name=name)
                lifestyle_objs.append(obj)
            instance.lifestyle_choices.set(lifestyle_objs)

        return instance    

class MyUserSerializer(serializers.ModelSerializer):
    # profile = ProfileSerializer(required=False)
    phone_no = serializers.CharField()
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

class VerifyUserSerializer(serializers.Serializer):

    email = serializers.EmailField()
    otp = serializers.CharField()

class TimelineSerializer(serializers.ModelSerializer):
    images_list = ImageSerializer(source='images', many=True, read_only=True)
    interests_list = InterestSerializer(many=True, source='interests', read_only=True)
    age = serializers.ReadOnlyField()            # from the model property
    distance = serializers.FloatField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'user_id', 'id', 'first_name', 'profile_pic', 'dob', 
            'bio', 'location', 'distance',
            'interests_list', 'images_list','age',
        ]

class OppUserDetailSerializer(serializers.ModelSerializer):

    interests_list = InterestSerializer(many=True, read_only=True)  # for read
    lifestyle_list = LifestyleSerializer(many=True, read_only=True)
    images_list = ImageSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'first_name', 'gender', 'last_name', 'profile_pic', 'dob', 'looking_for',
            'intention', 'sexual_orientation', 'show_orientation', 'bio', 'location', 
            'interests_list', 'images_list', 'latitude', 'longitude', 'social_links',
            'zodiac_sign', 'show_zodiac', 'lifestyle_list', 
        ]
        read_only_fields = [
            'id', 'first_name', 'gender', 'last_name', 'profile_pic', 'dob', 'looking_for',
            'intention', 'sexual_orientation', 'show_orientation', 'bio', 'location', 
            'interests_list', 'images_list', 'latitude', 'longitude', 'social_links',
            'zodiac_sign', 'show_zodiac', 'lifestyle_list', 
        ]


