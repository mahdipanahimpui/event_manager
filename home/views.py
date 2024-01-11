from django.shortcuts import HttpResponse
from django.views import View
from rest_framework import viewsets
from .serializers import EventSerializer
from utils.pagination import EventPagination
from .models import(
    Event
)

#-------------------------------------------------------------------
class HomeView(View):
    def get(self, request):
        return HttpResponse('hello world!')

# ----------------------------------------------------------------
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination



