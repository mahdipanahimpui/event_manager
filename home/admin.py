from django.contrib import admin
from .models import (
    Participant, 
    Event, 
    Meeting,
    Survey,
    Option,
    Opinion,
    SelectedOption,
)


admin.site.register(Participant)
admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Survey)
admin.site.register(Option)
admin.site.register(Opinion)
admin.site.register(SelectedOption)
