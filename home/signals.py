from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Participant

from django.core.mail import send_mail, EmailMessage
from event_manager.settings import EMAIL_HOST_USER

@receiver(pre_save, sender=Participant)
def handle_null_field_filled(sender, instance, **kwargs):
    attendance_time = instance.attendance_time
    # print('*'*90)
    # print('email_sending')

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        print(old_instance.attendance_time)
        print(instance.attendance_time)

        if old_instance.attendance_time is None and instance.attendance_time is not None:

            subject = f'{instance.event.name}'
            message = f'{instance.first_name} {instance.last_name} عزیز حضور شما ثبت شد'
            recipient_list = [instance.email_address]
            send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)
            # print('*'*90)
            # print('email sent')
    
    except sender.DoesNotExist:
        pass


