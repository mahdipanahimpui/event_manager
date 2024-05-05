from django.contrib import admin
from .models import Participant, Event, Meeting


admin.site.register(Participant)
admin.site.register(Event)
admin.site.register(Meeting)