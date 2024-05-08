from django.shortcuts import HttpResponse
from django.views import View

from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.generics import get_object_or_404

from django.core.mail import send_mail
from event_manager.settings import EMAIL_HOST_USER


from .serializers import (
    EventSerializer,
    ParticipantSerializer,
    MeetingSerializer,
    SurveySerializer, 
    SurveyOptionSerializer,
    SurveyOpinionSerializer,
    SurveySelectOptionSerializer
)

from utils.pagination import (
    EventPagination,
    ParticipantPagination,
    MeetingPagination,
    SurveyPagination,
    SurveyOptionPagination,
    SurveyOpinionPagination,
    SurveySelectOptionPagination
)

from .models import(
    Event,
    Participant,
    Meeting,
    Survey,
    Option,
    Opinion,
    SelectOption
)

# -------------------------------------------------------------------
class HomeView(View):
    def get(self, request):
        return HttpResponse('hello world!')

# -----------------------------------------------------------------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination   

# --------------------------------------------------------------------
class ParticipantListCreateView(generics.ListCreateAPIView):
    serializer_class = ParticipantSerializer
    pagination_class = ParticipantPagination

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Participant.objects.filter(event__id=event_id)
        return queryset
    
# -------------------------------------------------------------------
class ParticipantRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ParticipantSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Participant.objects.filter(event__id=event_id)
        return queryset

    def get_object(self):
        participant_id = self.kwargs['participant_id']
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=participant_id)
        return obj
    
# ----------------------------------------------------------------------
class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = MeetingPagination 

# -------------------------------------------------------------meetings---------
class SendEmailView(APIView):

    def post(self, request):
        pass
            

# ----------------------------------------------------------------------
class SurveyListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveySerializer
    pagination_class = SurveyPagination

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        meeting_id = self.kwargs.get('meeting_id', None)
        queryset = Survey.objects.filter(event__id=event_id, meeting__id=meeting_id)
        return queryset
    
# ----------------------------------------------------------------------------
class SurveyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    def get_object(self):
        surey_id = self.kwargs['survey_id']
        obj = get_object_or_404(Survey, id=surey_id)
        return obj
    

# ----------------------------------------------------------------------------
class SurveyOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveyOptionSerializer
    pagination_class = SurveyOptionPagination

    def get_queryset(self):
        survey_id = self.kwargs['survey_id']
        queryset = Option.objects.filter(survey__id=survey_id)
        return queryset
    
# -----------------------------------------------------------------------------
class SurveyOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveyOptionSerializer
    queryset = Option.objects.all()

    def get_object(self):
        option_id = self.kwargs['option_id']
        obj = get_object_or_404(Option, id=option_id)
        return obj
    
# ----------------------------------------------------------------------------
class SurveyOpinionListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveyOpinionSerializer
    pagination_class = SurveyOpinionPagination

    def get_queryset(self):
        survey_id = self.kwargs['survey_id']
        queryset = Opinion.objects.filter(survey__id=survey_id)
        return queryset
    
# -----------------------------------------------------------------------------
class SurveyOpinionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveyOpinionSerializer
    queryset = Opinion.objects.all()


    def get_object(self):
        opinion_id = self.kwargs['opinion_id']
        obj = get_object_or_404(Opinion, id=opinion_id)
        return obj
    
# ------------------------------------------------------------------------------
class SurveySelectOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveySelectOptionSerializer
    pagination_class = SurveySelectOptionPagination
    queryset = SelectOption.objects.all()

# -------------------------------------------------------------------------------
class SurveySelectOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySelectOptionSerializer
    queryset = SelectOption.objects.all()

# -------------------------------------------------------------------------------
class SurveyOptionCounterView(APIView):
    def get(self, request, *args, **kwargs):
        
        try:
            survey_id = kwargs['survey_id']
            survey = get_object_or_404(Survey, id=survey_id)
            options = Option.objects.filter(survey=survey)
            option_count = []
            for option in options:
                selected_option_count = SelectOption.objects.filter(survey=survey, option=option).count()
                option_count.append(
                    {'option': option.id,
                    'count': selected_option_count}
                    )
            survey_data = {
                'survey': survey_id,
                'results': option_count
            }
            
            return Response(survey_data)
        
        except Survey.DoesNotExist:
            return Response(
                {'error': f'Survey with id: {survey_id} not found'},
                status=404
            )
        
# ----------------------------------------------------------------------------
class SurveyOpinionCounterView(APIView):
    def get(self, request, *args, **kwargs):
        
        try:
            survey_id = kwargs['survey_id']
            survey = get_object_or_404(Survey, id=survey_id)
            opinion_count = Opinion.objects.filter(survey=survey).count()
            survey_data = {
                'survey': survey_id,
                'results': {
                    'opinion_count': opinion_count
                }
            }
            
            return Response(survey_data)
        
        except Survey.DoesNotExist:
            return Response(
                {'error': f'Survey with id: {survey_id} not found'},
                status=404
            )
        
# ----------------------------------------------------------------------------
class SendEventSurveysView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            event_id = kwargs['event_id']
            event = get_object_or_404(Event, id=event_id)
            participants = Participant.objects.filter(event=event).exclude(attendance_time__isnull=True)
            
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

            data = {
                'event': event_id,
                'results': results
            }
            return Response(data)
        
        except Event.DoesNotExist:
            return Response(
                {'error': f'event with id: {event_id} not found'},
                status=404
            ) 
        
# ---------------------------------------------------------------------------
class SendMeetingSurveysView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            meeting_id = kwargs['meeting_id']
            meeting = get_object_or_404(Meeting, id=meeting_id)
            event = meeting.event
            participants = meeting.participants.all()
            print('*'*90)
            print(participants)
            print(meeting.title)
            
            results = []

            for participant in participants:

                subject = f'{event.name}'
                message = f'{participant.first_name} {participant.last_name} عزیز ممنون می‌شویم در نظرسنجی  {meeting.title}شرکت‌ کنید \n www.127.0.0.1:8000/participate_survey/?participant_id={participant.id}&event_id={event.id}&meeting_id={meeting_id}'

                recipient_list = [participant.email_address]
                send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)

                results.append(
                    {'participant': participant.id,
                    'email': participant.email_address}
                    )

            data = {
                'meeting': meeting_id,
                'results': results
            }
            return Response(data)
        
        except Event.DoesNotExist:
            return Response(
                {'error': f'event with id: {meeting_id} not found'},
                status=404
            ) 




