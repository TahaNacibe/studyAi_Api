from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.conf import settings
from rest_framework.permissions import AllowAny
from api.model.response_model import getResponseFromEndPoint
from api.utils.formate_data_for_ai import PDFTableExtractor

class SchedulePDFUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]

    def options(self, request, *args, **kwargs):
        response = Response()
        response["Access-Control-Allow-Origin"] = "https://www.studai.site"  # You can restrict to specific origin
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, x-api-key"
        return response
    def post(self, request):
        # API key check
        api_key = request.headers.get("x-api-key")
        if api_key != settings.API_SECRET_KEY:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # PDF file check
        pdf_file = request.FILES.get("file")
        if not pdf_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # get all user data 
        pdf_data = pdf_file.read()
        user_class = request.data.get('userClass')
        user_tasks = request.data.get('userTasks')
        preferences = request.data.get('preferences')
        models_and_tasks_priorities = request.data.get('modelsAndTasksPriorities')
        
        extractor = PDFTableExtractor(pdf_data)
        tables = extractor.extract_all_tables()        
        finalRes = getResponseFromEndPoint(
            tableData = tables,
            userClass = user_class,
            userTasks = user_tasks,
            preferences = preferences,
            modelsAndTasksPriorities = models_and_tasks_priorities,
        )
        return Response({"Data": f" {finalRes}"})

