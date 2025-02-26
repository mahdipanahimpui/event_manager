from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from . tasks import send_meeting_attendance_email_task
from event_manager.settings import EMAIL_HOST_USER



from home.models import (
    Event,
    Participant,
    Meeting,
    Survey,
    SelectOption,
    Opinion,
    Option,
    Document,
    EmailLog
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
            'num',
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
        read_only_fields = [*base_read_only_fields, 'event', 'qr_code', 'num']


    def validate_event_id(self, value):
        try:
            Event.objects.get(id=value)
        except Event.DoesNotExist:
            raise serializers.ValidationError("Invalid event_id:{value}. Event does not exist.")
        return value
    

    def validate(self, attrs):
        event_id = attrs.get('event_id')
        mobile_phone_number = attrs.get('mobile_phone_number')
        email_address = attrs.get('email_address')

        
        try:
            event = Event.objects.get(id=event_id)

            if Participant.objects.filter(event=event, mobile_phone_number=mobile_phone_number).exists():
                raise serializers.ValidationError(
                    f"Participant with the same mobile_phone_number: {mobile_phone_number} already exists for for this event with event: {event.name} with event_id: {event.id}."
                )

            if Participant.objects.filter(event=event, email_address=email_address).exists():
                raise serializers.ValidationError(
                    f"Participant with the same email_address: {email_address} already exists for this event with event: {event.name} with event_id: {event.id}."
                )
        
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
            'remove_participants',
            'survey_email_sent',
            'sending_attendance_email'
        ]

        read_only_fields = [*base_read_only_fields, 'participants']


    def validate(self, attrs):
        event = attrs.get('event')
        code = attrs.get('code')

        try:

            if Meeting.objects.filter(event=event, code=code).exists():
                raise serializers.ValidationError("meeting with the same code already exists for this event.")

        except Event.DoesNotExist:
            pass

 
        return super().validate(attrs)



    def update(self, instance, validated_data):
        add_participants = validated_data.pop('add_participants', [])
        remove_participants = validated_data.pop('remove_participants', [])

        meeting = super().update(instance, validated_data)


        for participant in add_participants:

            if participant not in meeting.participants.all():
                
                meeting.participants.add(participant)
                # if not participant.attendance_time: # NOTE: HASBUG
                #     participant.attendance_time = datetime.datetime.now(pytz.timezone('Asia/Tehran'))
                #     participant.save()
                try:
                    if meeting.sending_attendance_email:
                        send_meeting_attendance_email_task.delay(participant, meeting=meeting)
                
                except:
                    pass
            
            else:
                raise serializers.ValidationError(f"the participant with id: {participant.id} is already exists")

            


        for participant in remove_participants:

            if participant in meeting.participants.all():

                meeting.participants.remove(participant)

            else:
                raise serializers.ValidationError(f"the participant with id: {participant.id} is doesnt exists")

        return meeting
    

# -------------------------------------------------------------
class SurveySerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = '__all__'

# -------------------------------------------------------------
class SurveyOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = '__all__'

# ---------------------------------------------------------------
class SurveyOpinionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Opinion
        fields = '__all__'


    def validate(self, attrs):
        survey = attrs.get('survey')
        participant = attrs.get('participant')

        try:

            if Opinion.objects.filter(survey=survey, participant=participant).exists():
                raise serializers.ValidationError(f"The participant id:{participant.id} has already answered this survey")
            
            if survey.meeting is not None:
                if participant not in survey.meeting.participants.all():
                    raise serializers.ValidationError(f"The participant id:{participant.id} hasn`t participate in the meeting id:{survey.meeting.id}")
            else:
                if participant.event.id != survey.event.id:
                    raise serializers.ValidationError(f"The participant id:{participant.id} hasn`t participate in the event id:{survey.event.id}")

        except Opinion.DoesNotExist:
            pass

        return super().validate(attrs)
    
# ---------------------------------------------------------------
class SurveySelectOptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SelectOption
        fields = '__all__'
        

    def validate(self, attrs):
        survey = attrs.get('survey')
        participant = attrs.get('participant')
        option = attrs.get('option')


        try:

            if survey and survey.id != option.survey.id:
                raise serializers.ValidationError(f"the survey with id:'{survey.id}' does not have option with id:'{option.id}'")


            if SelectOption.objects.filter(survey=survey, participant=participant).exists():
                raise serializers.ValidationError(f"The participant with id:{participant.id} has already answered this survey")
            
            if survey and participant:
                if survey.meeting is not None:
                    if participant not in survey.meeting.participants.all():
                        raise serializers.ValidationError(f"The participant with id:{participant.id} hasn`t participate in the meeting id:{survey.meeting.id}")
                else:
                    if participant.event.id != survey.event.id:
                        raise serializers.ValidationError(f"The participant with id:{participant.id} hasn`t participate in the event id:{survey.event.id}")


        except SelectOption.DoesNotExist:
            pass

        return super().validate(attrs)


# -----------------------------------------------------
class UserSerializer(serializers.ModelSerializer):        
    confirm_password = serializers.CharField(max_length=128, required=False, write_only=True)
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'is_active',
            'is_staff',
            'is_superuser',
            'username',
            'password', # the model hashed password, replaced with serializer field
            'confirm_password',
            'is_superuser',
            'email',
            'first_name',
            'last_name',
            'last_login',
            'date_joined',
            'groups',
            'user_permissions'

        ]
        read_only_fields = [
            'id',
            'last_login',
            'is_superuser',
            'is_staff',
            'date_joined',
            'groups',
            'user_permissions',
        ]

    def is_password_strong(self, password):
            validate_password(password)
            return True


    def check_passwords(self, password, confirm_password):
        if password:
            if confirm_password:
                if password != confirm_password:
                    raise serializers.ValidationError("passwords must match.")
            else:
                raise serializers.ValidationError("confirm_password field is requied")
            self.is_password_strong(password)
            return True
        return False
        

    def validate_activation(self, user, validated_data):
        is_active = validated_data.pop('is_active', None)
        # super user can change the is_active of all user except itself
        # all users even super user cant chage is_active of themselves
        if is_active is not None and (self.context['request'].user.is_superuser and user != self.context['request'].user):
            validated_data['is_active'] = is_active
        return validated_data
    

    def set_user_password(self, user, validated_data):
        password = validated_data.get('password', None)
        if password:
            user.set_password(validated_data['password'])
            user.save()
        return user


    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password', None)
        self.check_passwords(password, confirm_password)
        return super().validate(attrs)
    

    def create(self, validated_data):
        validated_data['is_active'] = validated_data.get('is_active', True)
        is_superuser = validated_data.get('is_superuser', False)

        user = super().create(validated_data)
        user = self.set_user_password(user, validated_data)

        if is_superuser:
            user.is_superuser = is_superuser
            user.is_staff = is_superuser
            user.save()
        return user


    def update(self, user, validated_data):
        validated_data = self.validate_activation(user, validated_data)
        user = super().update(user, validated_data)
        user = self.set_user_password(user, validated_data)
        return user
    

# -----------------------------------------------------------------------------------

class SendEmailSerializer(serializers.Serializer):
    subject = serializers.CharField()
    title = serializers.CharField()
    text = serializers.CharField(style={'base_template': 'textarea.html'})
    is_name_at_first = serializers.BooleanField()


# -----------------------------------------------------------------------------------
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

# -----------------------------------------------------------------------------------
class EmailLogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = [
            'id', 
            'event',
            'meeting',
            'when',
            'to',
            'subject',
            'title',
        ]

    def to_representation(self, instance):
        rep = super(EmailLogListSerializer, self).to_representation(instance)
        rep['event'] = instance.event.name
        if instance.meeting:
            rep['meeting'] = instance.meeting.code 

        return rep
    
# -----------------------------------------------------------------------------------
class EmailLogRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailLog
        fields = '__all__'

    def to_representation(self, instance):
        rep = super(EmailLogRetrieveSerializer, self).to_representation(instance)
        rep['event'] = instance.event.name
        if instance.meeting:
            rep['meeting'] = instance.meeting.code 

        return rep

    






