from .models import Client
from .models import Profile
from .models import Service
from .models import Testimonial
from django.contrib.auth.models import User
from rest_framework import serializers


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('name', 'description', 'icon')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class ProfileSerializer(serializers.ModelSerializer):
    # https://github.com/tomchristie/django-rest-framework/issues/1984#issuecomment-60267220
    user = UserSerializer()

    class Meta:
        model = Profile
        depth = 1
        fields = ('get_avatar_url', 'get_username', 'bio', 'user')


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = ('name', 'description', 'icon')


class TestimonialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Testimonial
        fields = ('name', 'slug', 'title', 'description', 'issue_date')
