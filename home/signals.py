from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Participant
from .tasks import send_event_attendanceـemailـtask
from event_manager.settings import EMAIL_HOST_USER
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import os


def qr_code_generator(id, num, phone, qr_code_field):
        qrcode_img = qrcode.make(f'num{num}_id{id}')
        canvas = Image.new('RGB', (295, 295), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'num{num}_id{id}_phone{phone}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        qr_code_field.save(fname, File(buffer), save=False)
        canvas.close()


@receiver(pre_save, sender=Participant)
def handle_null_field_filled(sender, instance, *args, **kwargs):
    try:
        old_instance = sender.objects.get(pk=instance.pk)

        if old_instance.attendance_time is None and instance.attendance_time is not None:

            send_event_attendanceـemailـtask.delay(instance)

    except sender.DoesNotExist:
        pass



@receiver(post_save, sender=Participant)  
def generate_qr_code_on_create(sender, instance, created, **kwargs):

  if created:
    # Only generate QR code if object was just created
        
    # Call QR code generator function
    qr_code_generator(instance.id, instance.num, instance.mobile_phone_number, 
                      instance.qr_code)

    # Save model to update QR code field  
    instance.save()



@receiver(pre_save, sender=Participant)
def capitalize_filed(sender, instance, **kwargs):
    instance.first_name = instance.first_name.capitalize()
    instance.last_name = instance.last_name.capitalize()


@receiver(pre_save, sender=Participant)
def lower_field(sender, instance, **kwargs):
    instance.regestered_as = instance.regestered_as.lower()
    instance.title = instance.title.lower()
    instance.education_level = instance.education_level.lower()
    instance.science_ranking = instance.science_ranking.lower()
    instance.membership_type = instance.membership_type.lower()
    instance.city = instance.city.lower()
    instance.email_address = instance.email_address.lower()



