from rest_framework.views import APIView
from rest_framework.response import Response
from tools.models.base import Tool
from tools.serializers.base import ToolSerializer

    
class HealthCheckAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "message": "Echo backend is running."})

class ToolListAPIView(APIView):
    def get(self, request):
        tools = Tool.objects.filter(is_active=True)
        serializer = ToolSerializer(tools, many=True, context={'request': request})
        return Response(serializer.data)