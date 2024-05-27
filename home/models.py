from django.db import models
from utils import validators
from rest_framework import serializers
import os
import re
from functools import partial
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError


# ----------------------------------------------------------------------------
def validate_max_file_size(value, max_size):
    # max_size = 10 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(f"The file size should not exceed {max_size} bytes.")
   

# ------------------------------------------------------------------------------------- 
def validate_uniqueness_by_event(event, field, field_name):
    existing_fields = Participant.objects.filter(event=event).values_list(f'{field_name}', flat=True)

    if str(field) in existing_fields:
        raise serializers.ValidationError(
            f"Participant with the same {field_name}: {field} already exists for this event with event: {event.name} with event_id: {event.id}, or imported twice"
        )
        # raise ValueError(f"Participant with the same {field_name} already exists for this event.")

# -------------------------------------------------------------------------------------
def validate_choice_field(field, field_name, choices):
    if field not in dict(choices).keys():
        raise serializers.ValidationError(
            f"invalid {field_name}: '{field}' "
        )
    
# --------------------------------------------------------------------------------------
def validate_email_regex(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not (re.fullmatch(regex, str(email) )):
        raise serializers.ValidationError(
            f"Participant with email: '{email}' is not valid."
        )
    
# --------------------------------------------------------------------------------------
def validate_phone_number_regex(mobile_phone_number):
    regex = r'^[+]?[0-9]*$'
    if not (re.fullmatch(regex, str(mobile_phone_number) )):
        raise serializers.ValidationError(
            f"Participant with mobile_phone_number: '{mobile_phone_number}' is invalid, mobile_hone_number must be digits. (+) can be at first"
        )
    
# -------------------------------------------------------------------------------------
def validate_integer_range(field_value,  field_name, min, max):
    pattern = r'^[\d]+$'

    if field_value and not bool(re.match(pattern, field_value)):
        raise serializers.ValidationError(
            f"Participant with {field_name}: '{field_value}' must be digit. min value: {min}, max value: {max}"
            )

    if field_value and not (min <= field_value <= max):
        raise serializers.ValidationError(
            f"Participant with {field_name}: '{field_value}' is not valid. min value: {min}, max value: {max}"
        )
    
# -------------------------------------------------------------------------------------
def validate_required_fields(instance, required_fileds):

    for field_name in required_fileds:
        field_value = getattr(instance, field_name)

        
        if field_value is None:
            raise serializers.ValidationError(
                f"the field {field_name} with email: '{instance.email_address}' is required or provided in incorect way"
            )
        
        if not str(field_value).strip():
            raise serializers.ValidationError(
                f"the field {field_name} with email: '{instance.email_address}' is required or provided in incorect way"
            )


#----------------------------------------------------------------------------------
def get_upload_path(instance, file_name):
    directory_name = f'eventid{instance.event.id}_{instance.event.name}'
    return os.path.join('qr_codes', directory_name, file_name)

# ------------------------------------------------------------------
# --------------------- MODELS ------------------------------------
# ------------------------------------------------------------------
class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)

    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    note = models.TextField(max_length=2000, null=True, blank=True)

    survey_email_sent = models.BooleanField(default=False)
    sending_attendance_email = models.BooleanField()

    def __str__(self):
        return str(self.name)

# -----------------------------------------------------------------
class Participant(models.Model):
    # seceond element is human-readable
    MEMBERSHIP_TYPE_CHOICES = (
        ('ordinary_author', 'ordinary_author'),
        ('student_author', 'student_author'),
        ('ut_student', 'ut_student'),
        ('ordinary_sutudent', 'ordinary_student'),
        ('free_participant', 'free_participant')
    )
    EDUCATION_LEVEL_CHOICES = (
        ('phd', 'phd'),
        ('md', 'md'),
        ('phd_candinate', 'phd_candinate'),
        ('masters', 'masters'),
        ('masters_student', 'masters_student'),
        ('bachelors', 'bachelors'),
        ('bachelor_student', 'bachelor_student'),
        ('other', 'other')
    )
    REGESTERED_AS_CHOICES = (
        ('individual', 'individual'),
        ('entity', 'entity'),
    )
    TITLE_CHOICES = (
        ('mr', 'mr'),
        ('mrs', 'mrs'),
        ('dr', 'dr')
    )
    SCIENCE_RANKING_CHOICES = (
        ('professor', 'professor'),
        ('assistant_professor', 'assistant_professor'),
        ('associated_professor', 'associated_professor'),
        ('other', 'other')
    )



    num = models.IntegerField(blank=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    regestered_as = models.CharField(max_length=30, choices=REGESTERED_AS_CHOICES)
    title = models.CharField(max_length=30, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    education_level = models.CharField(max_length=30, choices=EDUCATION_LEVEL_CHOICES)
    science_ranking = models.CharField(max_length=30, choices=SCIENCE_RANKING_CHOICES)
    # favorite_research_field = models.TextField(max_length=200, null=True, blank=True)
    # phone_number = models.CharField(max_length=15, validators=[validators.just_number_validator])
    # fax = models.CharField(max_length=20, null=True, blank=True)
    mobile_phone_number = models.CharField(max_length=15, validators=[validators.just_number_validator])
    # website = models.CharField(max_length=200, null=True, blank=True)
    membership_type = models.CharField(max_length=30, choices=MEMBERSHIP_TYPE_CHOICES)
    city = models.CharField(max_length=100)
    # postal = models.CharField(max_length=100, validators=[validators.just_number_validator])
    # organizational_affiliation = models.TextField(max_length=200)
    email_address = models.EmailField(max_length=200)
    # username = models.CharField(max_length=200)
    # description = models.TextField(max_length=500, null=True, blank=True)
    meal = models.SmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(2)])
    qr_code =  models.ImageField(upload_to=get_upload_path, blank=True)
    attendance_time = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if self._state.adding: 
            """
                these validations are used when creation instances form xlsx file
            """
            validate_required_fields(self, required_fileds=[
                'event', 'regestered_as', 'title', 'first_name', 'last_name', 'education_level', 'science_ranking', 'mobile_phone_number', 'membership_type', 'city', 'email_address', 'meal'
            ])
            validate_uniqueness_by_event(self.event, self.mobile_phone_number, 'mobile_phone_number')
            validate_uniqueness_by_event(self.event, self.email_address, 'email_address')
            validate_choice_field(self.membership_type, 'membership_type', choices=self.MEMBERSHIP_TYPE_CHOICES)
            validate_choice_field(self.education_level, 'education_level', choices=self.EDUCATION_LEVEL_CHOICES)
            validate_choice_field(self.regestered_as, 'regestered_as', choices=self.REGESTERED_AS_CHOICES)
            validate_choice_field(self.title, 'title', choices=self.TITLE_CHOICES)
            validate_choice_field(self.science_ranking, 'science_ranking', choices=self.SCIENCE_RANKING_CHOICES)
            validate_phone_number_regex(self.mobile_phone_number)
            validate_email_regex(self.email_address)
            validate_integer_range(self.meal, field_name='meal', min=0, max=2)

            self.num = Participant.objects.filter(event=self.event).count() + 1


        super().save(*args, **kwargs)

    
    def __str__(self):
        return str(self.email_address)
    
# ----------------------------------------------------------------------------------------
class Meeting(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    code = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    holding_time = models.DateTimeField()
    presenter = models.CharField(max_length=200)
    about_presenter = models.TextField(max_length=1000, null=True, blank=True)
    organizer = models.CharField(max_length=200, null=True, blank=True)
    holding_place = models.TextField(max_length=500)
    participants = models.ManyToManyField(Participant)
    survey_email_sent = models.BooleanField(default=False)
    sending_attendance_email = models.BooleanField()



    def __str__(self):
        return f'cod: {self.code}  |  title: {self.title}'

# ----------------------------------------------------------------------------------------
class Survey(models.Model):
    text = models.TextField(max_length=1000)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.pk}  |  {self.text}'


# -----------------------------------------------------------------------------------------
class Option(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=200)

    def __str__(self):
        return f'survey: {self.survey.pk}  |  option: {self.option_text}'

# ----------------------------------------------------------------------------------------
class SelectOption(models.Model):
    
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)



    def clean(self):
        if self.survey.pk != self.option.survey.pk:
            raise ValidationError(f"the survey with id:'{self.survey.pk}' does not have option with id:'{self.option.pk}'")
        
        if SelectOption.objects.filter(participant=self.participant, survey=self.survey).exists():
            raise ValidationError("The participant has already answered this survey")
        
        return super().clean()

    def __str__(self):
        return f'participant: {self.participant.email_address}  |  survey: {self.survey.id}  |  option: {self.option.option_text}'


# ------------------------------------------------------------------------------------------
class Opinion(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    opinion_text = models.TextField(max_length=1000)

    def __str__(self):
        return f'participant: {self.participant.email_address}  |  survey: {self.survey.pk}  |  opinion: {self.pk}'


    class Meta:
        unique_together = ('participant', 'survey')



# --------------------------------------------------------------------------------------------
class Document(models.Model):
    file = models.FileField(upload_to='documents/', validators=[
        partial(validate_max_file_size, max_size=10 * 1024 * 1024),
        FileExtensionValidator(allowed_extensions=['xlsx']),
    ])



# --------------------------------------------------------------------------------------------
class EmailLog(models.Model):
    """
    Model to store all the outgoing emails.
    """
    when = models.DateTimeField(auto_now_add=True)
    to = models.EmailField(max_length=256)
    subject = models.CharField(null=True, blank=True, max_length=256)
    title = models.CharField(null=True, blank=True, max_length=256)
    body = models.TextField(max_length=2048)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    meeting = models.ForeignKey(Meeting, null=True, blank=True, on_delete=models.CASCADE)





















