from django.urls import path
from .views import SchedulePDFUploadView

urlpatterns = [
    path('upload/', SchedulePDFUploadView.as_view(), name='upload'),
]
