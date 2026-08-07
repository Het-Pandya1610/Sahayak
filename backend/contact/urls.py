from django.urls import path
from .views import send_contact_email,report_misinformation

urlpatterns = [
    path('', send_contact_email, name='send_contact_email'),
    path('report-misinformation/', report_misinformation, name='report_misinformation'),
]