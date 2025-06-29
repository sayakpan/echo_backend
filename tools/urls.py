from django.urls import path

from tools.views.base import HealthCheckAPIView, ToolListAPIView
from .views import analyser, meta, schema

urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
    path('all/', ToolListAPIView.as_view(), name='tool-list'),
    path('analyser/<slug:slug>/', analyser.SchoolAnalyserAPIView.as_view(), name='school-analyser'),
    # path('meta-tester/', meta.MetaTagTesterAPIView.as_view(), name='meta-tester'),
    # path('schema-analyser/', schema.SchemaAnalyserAPIView.as_view(), name='schema-analyser'),
]
