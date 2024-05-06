from django.shortcuts import HttpResponse
from django.views import View

from rest_framework import viewsets, generics
from rest_framework.views import APIView

from rest_framework.generics import get_object_or_404


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
    SelectedOption
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

# ----------------------------------------------------------------------
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
    queryset = SelectedOption.objects.all()

# -------------------------------------------------------------------------------
class SurveySelectOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySelectOptionSerializer
    queryset = SelectedOption.objects.all()



