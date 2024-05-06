from django.urls import path
from . import views
from rest_framework import routers
# from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home_view'),
    path('events/<int:event_id>/participants/', views.ParticipantListCreateView.as_view(), name='participant_list_create_view'),
    path('events/<int:event_id>/participants/<int:participant_id>/', views.ParticipantRetrieveUpdateDestroyView.as_view(), name='participant_retrieve_update_destroy_view'), 
    # path('events/<int:event_id>/attended/<int:participant_id>', views.ParticipantsAttendanceView.as_view(), name='participants_attendance view')
    path('events/send_email/', views.SendEmailView.as_view(), name='send_email_view'),

    path('events/<int:event_id>/surveys/', views.SurveyListCreateView.as_view(), name='event_survey_list_create_view'),
    path('events/<int:event_id>/meetings/<int:meeting_id>/surveys/', views.SurveyListCreateView.as_view(), name='meeting_survey_list_create_view'),

    path('surveys/<int:survey_id>/', views.SurveyRetrieveUpdateDestroyView.as_view(), name='survey_retrieve_update_destroy_view'),

    path('surveys/<int:survey_id>/options/', views.SurveyOptionListCreateView.as_view(), name='survey_option_list_create_view'),
    path('options/<int:option_id>/', views.SurveyOptionRetrieveUpdateDestroyView.as_view(), name='survey_option_retrieve_update_destroy_view'),

    path('surveys/<int:survey_id>/opinions/', views.SurveyOpinionListCreateView.as_view(), name='survey_opinion_list_create_view'),
    path('survey_opinions/<int:opinion_id>/', views.SurveyOpinionRetrieveUpdateDestroyView.as_view(), name='survey_opinion_retrieve_update_destroy_view'),

    path('surveys/select_options/', views.SurveySelectOptionListCreateView.as_view(), name='survey_select_option_list_create_view'),
    path('survey_select_options/<int:select_option_id>/', views.SurveySelectOptionRetrieveUpdateDestroyView.as_view(), name='survey_select_option_retrieve_update_destroy_view'),


    

]

#-------------------------------------------------------------------
router = routers.SimpleRouter()
router.register('events', views.EventViewSet)
router.register('meetings', views.MeetingViewSet)

urlpatterns += router.urls
# ------------------------------------------------------------------

# spectacular_urlpatterns = [
#     # YOUR PATTERNS
#     path('schema/', SpectacularAPIView.as_view(), name='schema'),
#     # Optional UI:
#     path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
#     path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
# ]

# urlpatterns += spectacular_urlpatterns