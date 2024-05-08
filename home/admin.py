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
)

@admin.register(Participant)
class ParticipantModelAdmin(ImportExportModelAdmin):
    pass


admin.site.register(Event)
admin.site.register(Meeting)
admin.site.register(Survey)
admin.site.register(Option)
admin.site.register(Opinion)
admin.site.register(SelectOption)

