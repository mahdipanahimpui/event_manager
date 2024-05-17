from . emails import (
    send_event_survey_emails,
    send_meeting_survey_emails,
    send_email, 
    send_attendanceـemailـevent
)


# TODO: can be async
# ---------------------------------------------------------------------
def send_event_survey_emails_task(participants, event):
    result = send_event_survey_emails(participants, event)
    return result


# ---------------------------------------------------------------------
def send_meeting_survey_emails_task(participants, event, meeting):
    result = send_meeting_survey_emails(participants, event, meeting)
    return result


# ---------------------------------------------------------------------
def send_email_task(participants, validated_data):
    result = send_email(participants, validated_data)
    return result


# ---------------------------------------------------------------------
def send_attendanceـemailـevent_task(participant):
    send_attendanceـemailـevent(participant)
