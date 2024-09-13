from django.shortcuts import HttpResponse
from django.views import View
from django.contrib.auth import get_user_model
import pandas as pd
from django.db import IntegrityError, transaction
from utils.validators import check_file_extension, check_file_size
from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from permissions import IsSuperUser
from django.conf import settings
from event_manager.settings import EMAIL_HOST_USER
from django.http import HttpResponse
from openpyxl import Workbook
import numpy as np
from shutil import make_archive
from wsgiref.util import FileWrapper


from . tasks import (
    send_event_survey_email_task,
    send_meeting_survey_email_task,
    send_email_task
)



from . filtration import (
    Filtration, 
    ParticipantFiltration, 
    EventFiltration, 
    MeetingFiltration,
    UserFiltration,
    EmailLogFiltration
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
    DocumentSerializer,
    EmailLogListSerializer,
    EmailLogRetrieveSerializer
)

from utils.pagination import (
    EventPagination,
    ParticipantPagination,
    MeetingPagination,
    SurveyPagination,
    SurveyOptionPagination,
    SurveyOpinionPagination,
    SurveySelectOptionPagination,
    AdminPagination, 
    EmailLogPagination
)

from .models import(
    Event,
    Participant,
    Meeting,
    Survey,
    Option,
    Opinion,
    SelectOption,
    Document,
    EmailLog
)

# -------------------------------------------------------------------
class HomeView(View):
    def get(self, request):
        return HttpResponse('this is event manager')

# -----------------------------------------------------------------
class EventViewSet(Filtration ,viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    pagination_class = EventPagination   
    filtration_class = EventFiltration

    def destroy(self, request, *args, **kwargs):
        if self.request.method == 'DELETE' and not self.request.user.is_superuser:
            raise PermissionDenied('just superuser can delete the event')
    
        return super().destroy(request, *args, **kwargs)

# --------------------------------------------------------------------
class ParticipantListCreateView(Filtration, generics.ListCreateAPIView):
    serializer_class = ParticipantSerializer
    pagination_class = ParticipantPagination
    filtration_class = ParticipantFiltration
    

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Participant.objects.filter(event__id=event_id)
        queryset = self.filtration_class().list(self.request, queryset)
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
class MeetingListCreateView(Filtration, generics.ListCreateAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer
    pagination_class = MeetingPagination 
    filtration_class = MeetingFiltration

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Meeting.objects.filter(event__id=event_id)
        queryset = self.filtration_class().list(self.request, queryset)
        return queryset
    

# ----------------------------------------------------------------------
class MeetingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    def get_object(self):
        meeting_id = self.kwargs['meeting_id']
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=meeting_id)
        return obj

    def destroy(self, request, *args, **kwargs):
        if self.request.method == 'DELETE' and not self.request.user.is_superuser:
            raise PermissionDenied('just superuser can delete the meeting')
    
        return super().destroy(request, *args, **kwargs)


# -------------------------------------------------------------  ---------
class SendEmailView(Filtration, generics.GenericAPIView):
    permission_classes = [IsSuperUser]
    filtration_class = ParticipantFiltration
    

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = Participant.objects.filter(event__id=event_id)
        queryset = self.filtration_class().list(self.request, queryset)
        return queryset
    
    def post(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            participants = self.get_queryset()

            send_email_task.delay(participants, validated_data)
            
            data = {
                'event': event_id,
                'event_name': event.name, 
                'sending_to': list(participants.values_list("email_address", flat=True))
            }
            return Response(data) # status code NOTE
        
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
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super().get_permissions()
    
# ----------------------------------------------------------------------------
class SurveyRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    def get_object(self):
        surey_id = self.kwargs['survey_id']
        obj = get_object_or_404(Survey, id=surey_id)
        return obj
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super().get_permissions()
    

# ----------------------------------------------------------------------------
class SurveyOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveyOptionSerializer
    pagination_class = SurveyOptionPagination

    def get_queryset(self):
        survey_id = self.kwargs['survey_id']
        queryset = Option.objects.filter(survey__id=survey_id)
        return queryset
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return super().get_permissions()
    
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
        if self.request.method in ['PATCH', 'PUT', 'DELETE'] and not self.request.user.is_superuser:
            raise PermissionDenied('just superuser can update or delete the opinion')
        return super().get_permissions()
    
# ------------------------------------------------------------------------------
class SurveySelectOptionListCreateView(generics.ListCreateAPIView):
    serializer_class = SurveySelectOptionSerializer
    pagination_class = SurveySelectOptionPagination
    queryset = SelectOption.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        return super().get_permissions()

# -------------------------------------------------------------------------------
class SurveySelectOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SurveySelectOptionSerializer
    queryset = SelectOption.objects.all()

    def get_object(self):
        select_option_id = self.kwargs['select_option_id']
        obj = get_object_or_404(SelectOption, id=select_option_id)
        return obj

    def get_permissions(self): 
        if self.request.method in ['PATCH', 'PUT', 'DELETE'] and not self.request.user.is_superuser:
            raise PermissionDenied('just superuser can update or delete the select_option')
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
                     'option_text': option.option_text,
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
            
            send_event_survey_email_task.delay(participants, event)

            data = {
                'event': event_id,
                'event_name': event.name,
                'sending_to': list(participants.values_list("email_address", flat=True))
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
    
            send_meeting_survey_email_task.delay(participants, event, meeting)

            data = {
                'meeting': meeting_id,
                'meeting_code': meeting.code,
                'sending_to': list(participants.values_list("email_address", flat=True))
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
    filtration_class = UserFiltration
    pagination_class = AdminPagination

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
    



# --------------------------------------------------------------------------------------------------
class ExportView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        event = Event.objects.get(id=event_id)


        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename="{Participant.__name__}.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = f"{Participant.__name__}"

        # Add headers
        headers = [field.name for field in Participant._meta.fields]
        ws.append(headers)


        # Add data from the model
        participants = Participant.objects.filter(event=event)

        for p in participants:
            qr_code = p.qr_code.url if p.qr_code else None
            attendance_time = p.attendance_time.replace(tzinfo=None) if p.attendance_time else None
            created_at = p.created_at.replace(tzinfo=None) if p.created_at else None
            updated_at = p.updated_at.replace(tzinfo=None) if p.updated_at else None

            ws.append([
                p.id,
                p.num,
                p.event.name,
                p.regestered_as,
                p.title,
                p.first_name,
                p.last_name,
                p.education_level,
                p.science_ranking,
                p.mobile_phone_number,
                p.membership_type,
                p.city,
                p.email_address,
                p.meal,
                qr_code,
                attendance_time,
                created_at,
                updated_at
            ])

        # Save the workbook to the HttpResponse
        wb.save(response)
        return response
    

# ------------------------------------------------------------------------
class DocumentCreateView(generics.GenericAPIView):
    permission_classes = [IsSuperUser]
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def post(self, request, *args, **kwargs):
        event_id = kwargs['event_id']


        if 'file' in request.FILES:
            file  = request.FILES['file']

            if not check_file_extension(file, ['xlsx']):
                return Response(
                    {'message': 'the format supported is xlsx'},
                    status=status.HTTP_201_CREATED
                )
            
            if not check_file_size(file, 10):
                return Response(
                    {'message': 'max file size is 10MB'},
                    status=status.HTTP_201_CREATED
                )

            df = pd.read_excel(file, dtype={'mobile_phone_number': str})
            df = df.replace(np.nan, None)

            try:
                outer_index = None
                with transaction.atomic():
                    for index, row in df.iterrows():

                        try:
                            event = Event.objects.get(id=event_id)

                        except (Event.DoesNotExist, ValueError):
                            return Response(
                                    {'error': f"event with id: '{row['event']}' not found"},
                                    status=404
                                ) 
                        print(row)
                        instance = Participant(
                            event = event,
                            regestered_as = row['regestered_as'].strip().lower(),
                            title = row['title'].strip().lower(),
                            first_name = row['first_name'].strip().capitalize(),
                            last_name = row['last_name'].strip().capitalize(),
                            education_level = row['education_level'].strip().lower(),
                            science_ranking = row['science_ranking'].strip().lower(),
                            mobile_phone_number = str(row['mobile_phone_number']).strip(),
                            membership_type = row['membership_type'].strip().lower(),
                            city = row['city'].strip().lower(),
                            email_address = row['email_address'].strip().lower(),
                            meal = row['meal']
                        )

                        outer_index = index
                        instance.save()

                Document.objects.all().delete()

            except IntegrityError as e:
                raise (f"error at row{outer_index}") from e
            
            return Response(
                {'message': 'file uploaded and participant creation complete'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {'error': 'no file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )


# -------------------------------------------------------------------------
class DownloadQrcodeView(generics.GenericAPIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        event_id = kwargs['event_id']
        event = get_object_or_404(Event, id=event_id)
        qrcode_dir = f'{settings.MEDIA_ROOT}/qr_codes/eventid{event.id}_{event.name}'
        archive_file_name = f'{event.name}_qrcodes'
        
        path_to_zip = make_archive(qrcode_dir, "zip", qrcode_dir)
        response = HttpResponse(FileWrapper(open(path_to_zip,'rb')), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="{filename}.zip"'.format(
            filename = archive_file_name.replace(" ", "_")
        )
        return response
    

# --------------------------------------------------------------------------
class EmailLogListView(Filtration ,generics.ListAPIView):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogListSerializer
    filtration_class = EmailLogFiltration
    pagination_class = EmailLogPagination

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = EmailLog.objects.filter(event__id=event_id)
        queryset = self.filtration_class().list(self.request, queryset)
        return queryset
    
# --------------------------------------------------------------------------
class EmailLogRetrieveView(generics.RetrieveAPIView):
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogRetrieveSerializer

    def get_queryset(self):
        event_id = self.kwargs['event_id']
        queryset = EmailLog.objects.filter(event__id=event_id)
        return queryset
    
    def get_object(self):
        email_log_id = self.kwargs['email_log_id']
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=email_log_id)
        return obj
        
    

        
             