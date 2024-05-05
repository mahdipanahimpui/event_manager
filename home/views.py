from django.shortcuts import HttpResponse
from django.views import View

from rest_framework import viewsets, generics
from rest_framework.views import APIView

from rest_framework.generics import get_object_or_404



from .serializers import (
    EventSerializer,
    ParticipantSerializer,
    MeetingSerializer
)

from utils.pagination import (
    EventPagination,
    ParticipantPagination,
    MeetingPagination,
)

from .models import(
    Event,
    Participant,
    Meeting,
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


