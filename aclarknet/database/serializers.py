from .models import Client
from rest_framework import serializers


class ClientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Client
        fields = ('name', 'description')
