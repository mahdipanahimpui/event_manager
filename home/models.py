from django.db import models
from utils import validators

# ------------------------------------------------------------------
class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)

    start_date = models.DateField()
    end_date = models.DateField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
# -----------------------------------------------------------------

class Participant(models.Model):
    # image = 
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11, validators=[validators.phone_number_validator])
    email_address = models.EmailField()
    # membership_type = 
    # education_level = 
    # attributes = json field
    # qr_code = 
    attendance_time = models.DateTimeField()
# ------------------------------------------------------------------

class EventParticipants(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey('Participant', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('event', 'participant')



