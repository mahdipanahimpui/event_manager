from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Participant
from .tasks import send_attendanceـemailـevent_task
from event_manager.settings import EMAIL_HOST_USER

@receiver(pre_save, sender=Participant)
def handle_null_field_filled(sender, instance, *args, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)

        if old_instance.attendance_time is None and instance.attendance_time is not None:

            send_attendanceـemailـevent_task.delay(instance)

    except sender.DoesNotExist:
        pass


