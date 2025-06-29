from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tools.serializers.analyser import SchoolProfileScanSerializer
from tools.models.analyser import SchoolProfileScan
from tools.utils.analyser import analyse_school_profile, run_complete_school_analysis
import requests

class SchoolAnalyserAPIView(APIView):
    def get(self, request, slug):
        url = f"https://api.main.ezyschooling.com/api/v3/schools/{slug}/"
        res = requests.get(url)

        if res.status_code != 200:
            return Response({"error": "School not found"}, status=404)

        data = res.json()
        analysis = run_complete_school_analysis(slug, data)

        scan = SchoolProfileScan.objects.create(
            slug=slug,
            score=analysis.get("overall_score", 0),
            analysis=analysis,
        )

        serializer = SchoolProfileScanSerializer(scan)
        return Response(serializer.data)
