from django.core.mail import send_mail
from event_manager.settings import EMAIL_HOST_USER
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import EmailLog

# --------------------------------------------------------------------------
def send_event_survey_email(participants, event):

    for participant in participants:
        print(f"sending event (id: {event.id}, code: {event.name}) survey email to [{participant.email_address}] {'>'*5}", end='')

        subject = f'{event.name}'
        link = f'{settings.DOMAIN}/participate_survey/?participant_id={participant.id}&event_id={event.id}'
        title = 'نظرسنجی'
        
        context = {
            'participant': participant,
            'event': event,
            'link': link,
            'title': title
        }

        html_content = render_to_string('email_templates/event_survey.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        EmailLog.objects.create(to=recipient_list[0], subject=subject, body=html_content, event=event, title=title)

        print('sent OK')
    
    event.survey_email_sent = True
    event.save()

# --------------------------------------------------------------------------
def send_meeting_survey_email(participants, event, meeting):

    for participant in participants:
        print(f"sending meeting (id: {meeting.id}, code: {meeting.code}) survey email to [{participant.email_address}] {'>'*5}", end='')

        subject = f'{event.name}'
        link = f'{settings.DOMAIN}/participant_survey/?participant_id={participant.id}&event_id={event.id}&meeting_id={meeting.id}'
        title = 'نظرسنجی'
        context = {
            'participant': participant,
            'event': event,
            'meeting': meeting,
            'link': link,
            'title': title
        }

        html_content = render_to_string('email_templates/meeting_survey.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        EmailLog.objects.create(to=recipient_list[0], subject=subject, body=html_content, event=event, meeting=meeting, title=title)


        print('sent OK')
    
    meeting.survey_email_sent = True
    meeting.save()

# --------------------------------------------------------------------------
def send_email(participants, validated_data):

    for participant in participants:

        subject = f"{validated_data['subject']}"
        title = f"{validated_data['title']}"

        print(f"sending custom email (subject: {subject}, title: {title}) to [{participant.email_address}] {'>'*5}", end='')

        is_name_at_first = validated_data.get('is_name_at_first', False)
        text = f"{validated_data['text']}"
        title = f"{validated_data['title']}"

        context = {
            'participant': participant,
            'is_name_at_first': is_name_at_first,
            'text': text,
            'title': title
        }

        html_content = render_to_string('email_templates/custom_email.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        EmailLog.objects.create(to=recipient_list[0], subject=subject, body=html_content, event=participant.event, title=title)


        print('sent OK')

        
# --------------------------------------------------------------------------
def send_event_attendanceـemail(participant):

    if participant.event.sending_attendance_email:
        print(f"sending event (id: {participant.event.id}, event_name: {participant.event.name}) attendance email to [{participant.email_address}] {'>'*5}", end='')

        subject = f'{participant.event.name}'
        title = 'ثبت حضور'

        context = {
            'participant': participant,
            'event': participant.event, 
            'title': title
        }

        html_content = render_to_string('email_templates/event_attendance.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        EmailLog.objects.create(to=recipient_list[0], subject=subject, body=html_content, event=participant.event, title=title)

        print('sent OK')


# --------------------------------------------------------------------------
def send_meeting_attendance_email(participant, meeting):
    if meeting.sending_attendance_email:
        print(f"sending meeting (id: {meeting.id}, code: {meeting.code}) attendance email to [{participant.email_address}] {'>'*5}", end='')

        subject = f'{participant.event.name}'
        title = 'ثبت حضور'

        context = {
            'participant': participant,
            'meeting': meeting,
            'title': title
        }

        html_content = render_to_string('email_templates/meeting_attendance.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        EmailLog.objects.create(to=recipient_list[0], subject=subject, body=html_content, event=participant.event, meeting=meeting, title=title)

        print('sent OK')