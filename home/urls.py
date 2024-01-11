from django.urls import path
from . import views
from rest_framework import routers


app_name = 'home'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]

#-------------------------------------------------------------------
router = routers.SimpleRouter()
router.register('events', views.EventViewSet)

urlpatterns += router.urls
# ------------------------------------------------------------------