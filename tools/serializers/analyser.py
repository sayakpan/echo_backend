from rest_framework import serializers
from tools.models.analyser import SchoolProfileScan

class SchoolProfileScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolProfileScan
        fields = '__all__'
