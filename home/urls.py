from django.urls import path
from . import views
from rest_framework import routers


app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home_view'),
    path('events/<int:event_id>/participants/', views.ParticipantListCreateView.as_view(), name='participant_list_create_view'),
    path('events/<int:event_id>/participants/<int:participant_id>/', views.ParticipantRetrieveUpdateDestroyView.as_view(), name='participant_retrieve_update_destroy_view'), 
    # path('events/<int:event_id>/attended/<int:participant_id>', views.ParticipantsAttendanceView.as_view(), name='participants_attendance view')

]

#-------------------------------------------------------------------
router = routers.SimpleRouter()
router.register('events', views.EventViewSet)
router.register('meetings', views.MeetingViewSet)

urlpatterns += router.urls
# ------------------------------------------------------------------