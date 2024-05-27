from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Participant, 
    Event, 
    Meeting,
    Survey,
    Option,
    Opinion,
    SelectOption,
    EmailLog
)

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('num', 'event', 'id', 'regestered_as', 'title', 'first_name', 'last_name',
                    'education_level', 'science_ranking', 'mobile_phone_number',
                    'membership_type', 'city', 'email_address', 'meal', 'attendance_time')
    
    search_fields = ('num', 'id', 'regestered_as', 'title', 'first_name', 'last_name',
                    'education_level', 'science_ranking', 'mobile_phone_number',
                    'membership_type', 'city', 'email_address', 'meal')
    
    list_filter = ('event', 'regestered_as', 'title', 'education_level', 'science_ranking',
                   'membership_type', 'meal')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'start_date', 'end_date', 'sending_attendance_email', 'survey_email_sent', 'note')
    search_fields = ('name', 'start_date', 'note')
    list_filter =  ('is_active', 'sending_attendance_email', 'survey_email_sent')


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'code', 'title', 'holding_time', 'holding_place', 
                    'sending_attendance_email', 'survey_email_sent', 'presenter', 'organizer')
    search_fields = ('code', 'title', 'holding_place', 
                    'presenter', 'organizer', 'about_presenter')
    list_filter =  ('event', 'survey_email_sent', 'sending_attendance_email')
    raw_id_fields = ('participants', )


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'meeting', 'text')
    search_fields = ('meeting', 'text')
    list_filter = ('event',)
    raw_id_fields = ('event', 'meeting')

    
@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'option_text')
    search_fields = ('option_text',)
    list_filter = ('survey',)
    raw_id_fields = ('survey',)


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'participant', 'opinion_text',)
    search_fields = ('opinion_text',)
    list_filter = ('survey',)
    raw_id_fields = ('survey', 'participant')

@admin.register(SelectOption)
class SelectOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'participant', 'option')
    list_filter = ('survey',)
    raw_id_fields = ('survey', 'participant', 'option')



@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'meeting', 'to', 'subject', 'title')
    list_filter = ('event',)
    raw_id_fields = ('event', 'meeting')