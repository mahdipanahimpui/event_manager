from django.core.mail import send_mail
from event_manager.settings import EMAIL_HOST_USER


def send_event_survey_emails(participants, event):
    results = []

    for participant in participants:

        subject = f'{event.name}'
        message = f'{participant.first_name} {participant.last_name} عزیز ممنون می‌شویم در نظرسنجی  {event.name}شرکت‌ کنید \n www.127.0.0.1:8000/participate_survey/?participant_id={participant.id}&event_id={event_id}'

        recipient_list = [participant.email_address]
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)

        results.append(
            {'participant': participant.id,
            'email': participant.email_address}
            )
    
    return results