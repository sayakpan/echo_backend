from rest_framework import serializers
from tools.models.base import Tool


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'slug', 'short_description', 'logo', 'is_active']