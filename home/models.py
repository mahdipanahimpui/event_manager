from django.db import models
from utils import validators
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import os

from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError





# ------------------------------------------------------------------------------------- 
def validate_uniqueness_by_event(event, field, field_name):
    existing_fields = Participant.objects.filter(event=event).values_list(f'{field_name}', flat=True)
    if field in existing_fields:
        raise ValueError(f"Participant with the same {field_name} already exists for this event.")
    


def qr_code_generator(id, num, phone, qr_code_field):
        qrcode_img = qrcode.make(f'{id}')
        canvas = Image.new('RGB', (290, 290), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qr_code|id:{id}|num:{num}|phone{phone}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        qr_code_field.save(fname, File(buffer), save=False)
        canvas.close()


def get_upload_path(instance, file_name):
    directory_name = f'event_id:{instance.id}-start_date:{instance.start_date}'
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


    def clean(self):
        if Participant.objects.filter(event=self.event, phone_number=self.phone_number).exists():
            raise ValidationError("Participant with the same phone number already exists for this event.")


        if Participant.objects.filter(event=self.event, email_address=self.email_address).exists():
             raise ValidationError("Participant with the same email address already exists for this event.")
        
        return super().clean()




    def save(self, *args, **kwargs):
        if self._state.adding: 
            validate_uniqueness_by_event(self.event, self.mobile_phone_number, 'mobile_phone_number')
            validate_uniqueness_by_event(self.event, self.email_address, 'email_address')
            self.num = Participant.objects.filter(event=self.event).count() + 1

            super().save(*args, **kwargs)

            qr_code_generator(self.id, self.num, self.mobile_phone_number, self.qr_code)

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
    option_field = models.CharField(max_length=200)

    def __str__(self):
        return f'survey: {self.survey.pk}  |  option: {self.option_field}'

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
        return f'participant: {self.participant.email_address}  |  survey: {self.survey.id}  |  option: {self.option.option_field}'


# ------------------------------------------------------------------------------------------
class Opinion(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    opinion_text = models.TextField(max_length=1000)

    def __str__(self):
        return f'participant: {self.participant.email_address}  |  survey: {self.survey.pk}  |  opinion: {self.pk}'


    class Meta:
        unique_together = ('participant', 'survey')



























