from django.shortcuts import HttpResponse
from django.views import View
from django.contrib.auth import get_user_model


from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from .permissions import IsSuperUser

from event_manager.settings import EMAIL_HOST_USER


from . tasks import (
    send_event_survey_emails_task,
    send_meeting_survey_emails_task,
    send_email
)



from . filtration import (
    Filtration, 
    ParticipantFiltration, 
    EventFiltration, 
    MeetingFiltration
)


from .serializers import (
    EventSerializer,
    ParticipantSerializer,
    MeetingSerializer,
    SurveySerializer, 
    SurveyOptionSerializer,
    SurveyOpinionSerializer,
    SurveySelectOptionSerializer,
    UserSerializer, 
    SendEmailSerializer,

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
class EventViewSet(Filtration ,viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination   
    filtration_class = EventFiltration

# --------------------------------------------------------------------
class ParticipantListCreateView(Filtration ,generics.ListCreateAPIView):
    serializer_class = ParticipantSerializer
    pagination_class = ParticipantPagination
    filtration_class = ParticipantFiltration
    

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
class MeetingViewSet(Filtration ,viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = MeetingPagination 
    filtration_class = MeetingFiltration


# -------------------------------------------------------------  ---------
class SendEmailView(generics.GenericAPIView):
    # permission_classes = [AllowAny] ### NOTE: remove it
    filtration_class = ParticipantFiltration

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Participant.objects.filter(event__id=event_id)
        queryset = self.filtration_class().list(self.request, queryset)
        return queryset
    
    def post(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            participants = self.get_queryset()

            results = send_email.delay(participants, validated_data)
            
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
        





# ------------------------------  Survey ----------------------------------------
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
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return super().get_permissions()
    
# -----------------------------------------------------------------------------
class SurveyOpinionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveyOpinionSerializer
    queryset = Opinion.objects.all()

    def get_object(self):
        opinion_id = self.kwargs['opinion_id']
        obj = get_object_or_404(Opinion, id=opinion_id)
        return obj
    
    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsSuperUser]
        
        return super().get_permissions()
    
# ------------------------------------------------------------------------------
class SurveySelectOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveySelectOptionSerializer
    pagination_class = SurveySelectOptionPagination
    queryset = SelectOption.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny]
        return super().get_permissions()

# -------------------------------------------------------------------------------
class SurveySelectOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySelectOptionSerializer
    queryset = SelectOption.objects.all()

    def get_permissions(self):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsSuperUser]
        
        return super().get_permissions()
 

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
class SendEventSurveyEmailsView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request, *args, **kwargs):
        try:
            event_id = kwargs['event_id']
            event = get_object_or_404(Event, id=event_id)
            participants = Participant.objects.filter(event=event).exclude(attendance_time__isnull=True)
            
            results = send_event_survey_emails_task.delay(participants, event)

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
class SendMeetingSurveyEmailsView(APIView):
    permission_classes = [IsSuperUser]
    def get(self, request, *args, **kwargs):
        try:
            meeting_id = kwargs['meeting_id']
            meeting = get_object_or_404(Meeting, id=meeting_id)
            event = meeting.event
            participants = meeting.participants.all()
    
            results = send_meeting_survey_emails_task.delay(participants, event, meeting)

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

# ---------------------------------------------------------------------------
class AdminViewSet(Filtration, viewsets.ModelViewSet):
    permission_classes = [IsSuperUser]
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

# ----------------------------------------------------------------------------
class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(id=self.request.user.id)
        return queryset
    
    def get_object(self):
        return self.get_queryset().first()
    
    def delete(self, request, *args, **kwargs):
        raise PermissionDenied('you cant remvoe yourself, it will done only by the superuser ')