from django.core.mail import send_mail
from event_manager.settings import EMAIL_HOST_USER
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from urllib.parse import quote


# --------------------------------------------------------------------------
def send_event_survey_email(participants, event):
    # results = []

    for participant in participants:
        print(f"sending event (id: {event.id}, code: {event.name}) survey email to [{participant.email_address}] {'>'*5}", end='')

        subject = f'{event.name}'
        link = f'{settings.DOMAIN}/participate_survey/?participant_id={participant.id}&event_id={event.id}'
        
        context = {
            'participant': participant,
            'event': event,
            'link': link,
        }

        html_content = render_to_string('email_templates/event_survey.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print('sent OK')


    #     results.append(
    #         {'participant': participant.id,
    #         'email': participant.email_address}
    #         )
    
    # return results


# --------------------------------------------------------------------------
def send_meeting_survey_email(participants, event, meeting):
    # results = []

    for participant in participants:
        print(f"sending meeting (id: {meeting.id}, code: {meeting.code}) survey email to [{participant.email_address}] {'>'*5}", end='')

        subject = f'{event.name}'
        link = f'{settings.DOMAIN}/participate_survey/?participant_id={participant.id}&event_id={event.id}&meeting_id={meeting.id}'
        context = {
            'participant': participant,
            'event': event,
            'meeting': meeting,
            'link': link
        }

        html_content = render_to_string('email_templates/meeting_survey.html', context)
        recipient_list = [participant.email_address]

        msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print('sent OK')


    #     results.append(
    #         {'participant': participant.id,
    #         'email': participant.email_address}
    #         )
    
    # return results


# --------------------------------------------------------------------------
def send_email(participants, validated_data):
    # results = []

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

        print('sent OK')

        # results.append(
        #     {'participant': participant.id,
        #     'email': participant.email_address}
        #     )
        
        # return results
        
# --------------------------------------------------------------------------
def send_event_attendanceـemail(participant):

    print(f"sending event (id: {participant.event.id}, event_name: {participant.event.name}) attendance email to [{participant.email_address}] {'>'*5}", end='')

    subject = f'{participant.event.name}'

    context = {
        'participant': participant,
        'event': participant.event
    }

    html_content = render_to_string('email_templates/event_attendance.html', context)
    recipient_list = [participant.email_address]

    msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    print('sent OK')


# --------------------------------------------------------------------------
def send_meeting_attendance_email(participant, meeting):
    print(f"sending meeting (id: {meeting.id}, code: {meeting.code}) attendance email to [{participant.email_address}] {'>'*5}", end='')

    subject = f'{participant.event.name}'

    context = {
        'participant': participant,
        'meeting': meeting
    }

    # message = f"{participant.first_name} {participant.last_name} عزیز حضور شما در نشست با کد{meeting_code} ثبت شد"

    html_content = render_to_string('email_templates/meeting_attendance.html', context)
    recipient_list = [participant.email_address]

    msg = EmailMultiAlternatives(subject, html_content, settings.EMAIL_HOST_USER, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    print('sent OK')