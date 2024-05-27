from django.urls import path
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home_view'),
    path('events/<int:event_id>/participants/', views.ParticipantListCreateView.as_view(), name='participant_list_create_view'),
    path('events/<int:event_id>/participants/<int:participant_id>/', views.ParticipantRetrieveUpdateDestroyView.as_view(), name='participant_retrieve_update_destroy_view'), 
    path('events/<int:event_id>/send_email/', views.SendEmailView.as_view(), name='send_email_view'),
    path('events/<int:event_id>/export/', views.ExportView.as_view(), name='export_view'),
    path('events/<int:event_id>/import/', views.DocumentCreateView.as_view(), name='import_view'),
    path('events/<int:event_id>/meetings/', views.MeetingListCreateView.as_view(), name='meeting_list_create_view'),
    path('events/<int:event_id>/meetings/<int:meeting_id>/', views.MeetingRetrieveUpdateDestroyView.as_view(), name='meeting_retrieve_update_destroy_view'),



    path('events/<int:event_id>/surveys/', views.SurveyListCreateView.as_view(), name='event_survey_list_create_view'),
    path('events/<int:event_id>/meetings/<int:meeting_id>/surveys/', views.SurveyListCreateView.as_view(), name='meeting_survey_list_create_view'),
    path('events/<int:event_id>/send_surveys/', views.SendEventSurveyEmailsView.as_view(), name='send_event_suvey_emails_view'), # to present participants
    path('meetings/<int:meeting_id>/send_surveys/', views.SendMeetingSurveyEmailsView.as_view(), name='send_meeting_suvey_emails_view'),

    path('surveys/<int:survey_id>/', views.SurveyRetrieveUpdateDestroyView.as_view(), name='survey_retrieve_update_destroy_view'),
    path('surveys/<int:survey_id>/options/', views.SurveyOptionListCreateView.as_view(), name='survey_option_list_create_view'),
    path('surveys/<int:survey_id>/option_counter/', views.SurveyOptionCounterView.as_view(), name='surveys_option_counter_view'),

    path('options/<int:option_id>/', views.SurveyOptionRetrieveUpdateDestroyView.as_view(), name='survey_option_retrieve_update_destroy_view'),

    path('surveys/<int:survey_id>/opinions/', views.SurveyOpinionListCreateView.as_view(), name='survey_opinion_list_create_view'),
    path('surveys/opinions/<int:opinion_id>/', views.SurveyOpinionRetrieveUpdateDestroyView.as_view(), name='survey_opinion_retrieve_update_destroy_view'),

    path('surveys/select_options/', views.SurveySelectOptionListCreateView.as_view(), name='survey_select_option_list_create_view'),
    path('surveys/select_options/<int:select_option_id>/', views.SurveySelectOptionRetrieveUpdateDestroyView.as_view(), name='survey_select_option_retrieve_update_destroy_view'),
    path('surveys/<int:survey_id>/opinion_counter/', views.SurveyOpinionCounterView.as_view(), name='surveys_opinion_counter_view'),
    
    path('profile/', views.ProfileView.as_view(), name='profile_view'),

    path('events/<int:event_id>/qrcodes/', views.DownloadQrcodeView.as_view(), name='download_qrcode_view'),
    path('events/<int:event_id>/email_logs/', views.EmailLogListView.as_view(), name='email_log_list_view'),
    path('events/<int:event_id>/email_logs/<int:email_log_id>/', views.EmailLogRetrieveView.as_view(), name='email_log_retrieve_view'),

]

#-------------------------------------------------------------------
router = routers.SimpleRouter()
router.register('events', views.EventViewSet)
router.register('admins', views.AdminViewSet)


urlpatterns += router.urls
# ------------------------------------------------------------------


authentication_urls = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/token_refresh/', TokenRefreshView.as_view(), name='login_token_refresh'),
]

urlpatterns += authentication_urls