from rest_framework import serializers
from home import models




base_read_only_fields = [
    'id', 'created_at', 'updated_at'
]



class EventSerializer(serializers.ModelSerializer):

    class Meta: 
        model = models.Event
        fields = '__all__'
        read_only_fields = base_read_only_fields