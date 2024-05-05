from rest_framework import serializers
from django.shortcuts import get_object_or_404
import pyqrcode
from pyqrcode import QRCode
from home.models import (
    Event,
    Participant,
    Meeting
)

# ---------------------------------------------------
base_read_only_fields = [
    'id', 'created_at', 'updated_at'
]

# ---------------------------------------------------
class EventSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Event
        fields = '__all__'
        read_only_fields = base_read_only_fields

# ---------------------------------------------------
class ParticipantSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Participant
        fields = [
            'id',
            'event',
            'regestered_as',
            'title',
            'first_name',
            'last_name',
            'education_level',
            'science_ranking',
            'mobile_phone_number',
            'membership_type',
            'city',
            'email_address',
            'meal',
            'qr_code',
            'attendance_time',
            'created_at',
            'updated_at',
            'event_id'
        ]
        read_only_fields = [*base_read_only_fields, 'event', 'qr_code']


    def validate_event_id(self, value):
        try:
            Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Invalid event_id. Event does not exist.")
        return value
    

    def validate(self, attrs):
        event_id = attrs.get('event_id')
        phone_number = attrs.get('phone_number')
        email_address = attrs.get('email_address')

        
        try:
            event = Event.objects.get(id=event_id)

            if Participant.objects.filter(event=event, phone_number=phone_number).exists():
                raise serializers.ValidationError("Participant with the same phone number already exists for this event.")


            if Participant.objects.filter(event=event, email_address=email_address).exists():
                raise serializers.ValidationError("Participant with the same email address already exists for this event.")
        
        except Event.DoesNotExist:
            pass



        return super().validate(attrs)

    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        event = get_object_or_404(Event, id=event_id)

        participant = Participant.objects.create(event=event, **validated_data)

        return participant
    
# ------------------------------------------------------
class MeetingSerializer(serializers.ModelSerializer):

    add_participants = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Participant.objects.all()),
        write_only=True,
        required=False
    )

    remove_participants = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Participant.objects.all()),
        write_only=True,
        required=False
    )

    class Meta:
        model = Meeting
        fields = [
            'id',
            'event',
            'code',
            'title',
            'holding_time',
            'presenter',
            'about_presenter',
            'organizer',
            'holding_place',
            'participants',
            'add_participants',
            'remove_participants'
        ]

        read_only_fields = [*base_read_only_fields]


    def validate(self, attrs):
        event_id = attrs.get('event_id')
        code = attrs.get('code')

        try:
            event = Event.objects.get(id=event_id)

            if Participant.objects.filter(event=event, code=code).exists():
                raise serializers.ValidationError("meeting with the same code already exists for this event.")

        except Event.DoesNotExist:
            pass


        
       
        return super().validate(attrs)


    def update(self, instance, validated_data):
        add_participants = validated_data.pop('add_participants', [])
        remove_participants = validated_data.pop('remove_participants', [])

        meeting = super().update(instance, validated_data)


        for participant in add_participants:
            meeting.participants.add(participant)

        for participant in remove_participants:
            meeting.participants.remove(participant)

        return meeting