from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Participant

from django.core.mail import send_mail
from event_manager.settings import EMAIL_HOST_USER

@receiver(pre_save, sender=Participant)
def handle_null_field_filled(sender, instance, *args, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)

        if old_instance.attendance_time is None and instance.attendance_time is not None:

            subject = f'{instance.event.name}'
            message = f'{instance.first_name} {instance.last_name} عزیز حضور شما ثبت شد'
            recipient_list = [instance.email_address]
            send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)
    
    except sender.DoesNotExist:
        pass


