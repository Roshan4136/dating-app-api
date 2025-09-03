from rest_framework import serializers

class AbsoluteImageField(serializers.ImageField):
    """
    DRF ImageField that returns absolute URL including domain
    """
    def to_representation(self, value):
        if not value:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(value.url)
        return value.url  # fallback to relative URL

class AbsoluteFileField(serializers.FileField):
    def to_representation(self, value):
        if not value:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(value.url)
        return value.url    