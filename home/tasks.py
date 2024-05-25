from . emails import (
    send_event_survey_email,
    send_meeting_survey_email,
    send_email, 
    send_event_attendanceـemail,
    send_meeting_attendance_email
)
from celery import shared_task


# TODO: can be async
# ---------------------------------------------------------------------
@shared_task
def send_event_survey_email_task(participants, event):
    send_event_survey_email(participants, event)



# ---------------------------------------------------------------------
@shared_task
def send_meeting_survey_email_task(participants, event, meeting):
    send_meeting_survey_email(participants, event, meeting)
    


# ---------------------------------------------------------------------
@shared_task
def send_email_task(participants, validated_data):
    send_email(participants, validated_data)


# ---------------------------------------------------------------------
@shared_task
def send_event_attendanceـemailـtask(participant):
    send_event_attendanceـemail(participant)

# --------------------------------------------------------------------
@shared_task
def send_meeting_attendance_email_task(participant, meeting):
    send_meeting_attendance_email(participant, meeting)