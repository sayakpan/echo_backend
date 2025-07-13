import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
import re
import pandas as pd
from django.http import StreamingHttpResponse
import json

from tools.utils.scraper import extract_school_sections
from tools.utils.gemini import generate_parent_review, generate_static_review
from tools.utils.ratings import get_default_ratings
from tools.utils.review_submitter import submit_review


class EzyschoolingLoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        login_payload = {"email": email, "password": password}
        login_url = "https://api.horizon-dev.ezyschooling.com/api/v1/accounts/login/"

        login_response = requests.post(login_url, json=login_payload)
        if login_response.status_code != 200:
            return Response({"error": "Login failed"}, status=login_response.status_code)

        token = login_response.json().get("key")
        parent_url = "https://api.horizon-dev.ezyschooling.com/api/v1/parents/"
        parent_response = requests.get(parent_url, headers={"Authorization": f"Token {token}"})

        if parent_response.status_code != 200:
            return Response({"error": "Failed to fetch parent data"}, status=parent_response.status_code)

        parent_data = parent_response.json()
        return Response({
            "token": token,
            "user_id": parent_data.get("user"),
            "parent": parent_data
        })


class ReviewUploadExcelView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        token = request.data.get("token")
        user_id = request.data.get("user_id")

        if not uploaded_file or not token or not user_id:
            return Response({"error": "Missing file, token, or user_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            urls = []
            for col in df.columns:
                urls += df[col].dropna().astype(str).tolist()

            slugs = []
            for url in urls:
                match = re.search(r'/school/([^/]+)', url)
                if match:
                    slugs.append(match.group(1))

            print(f"Extracted slugs: {slugs}")

            if not slugs:
                return Response({"error": "No valid school profile URLs found."}, status=status.HTTP_400_BAD_REQUEST)

            def generate_reviews():
                for slug in slugs:
                    school_name = slug.replace("-", " ").title()
                    try:
                        section_data = extract_school_sections(f"https://ezyschooling.com/school/{slug}")
                        if not section_data:
                            raise ValueError("No content extracted from school profile.")

                        # result = generate_parent_review(school_name, section_data)
                        result = generate_static_review(school_name, section_data)
                        review_text = result.get("review", "Review generation failed.")
                        ratings = result.get("ratings", get_default_ratings())
                        submit = submit_review(slug, token, user_id, review_text, ratings)

                        result_data = {
                            "slug": slug,
                            "review": review_text,
                            "ratings": ratings,
                            "submitted": submit.get("success", False),
                        }
                    except Exception as e:
                        result_data = {
                            "slug": slug,
                            "submitted": False,
                            "error": str(e)
                        }

                    yield json.dumps(result_data) + "\n"

            return StreamingHttpResponse(generate_reviews(), content_type='application/x-ndjson')

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)