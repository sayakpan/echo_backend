from django.urls import path

from tools.views.base import HealthCheckAPIView, ToolListAPIView
from .views import analyser, reviewer

urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    path('all/', ToolListAPIView.as_view(), name='tool-list'),
    path('analyser/<slug:slug>/', analyser.SchoolAnalyserAPIView.as_view(), name='school-analyser'),
    path('reviewer/login/', reviewer.EzyschoolingLoginView.as_view(), name='school-reviewer-login'),
    path('reviewer/upload/', reviewer.ReviewUploadExcelView.as_view(), name='reviewer-upload'),
]
