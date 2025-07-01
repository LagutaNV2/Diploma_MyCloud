# storage/views.py
import os
import logging
from django.conf import settings
from django.utils import timezone
from django.shortcuts import render
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import File
from .serializers import FileSerializer, FileUploadSerializer
from .permissions import IsFileOwnerOrAdmin
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsFileOwnerOrAdmin]

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        # Для админа с user_id показываем файлы указанного пользователя
        if user_id and self.request.user.is_admin:
            return File.objects.filter(user_id=user_id)
        # Для всех пользователей (включая админа) возвращаем их файлы
        return File.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        # Удаление файла из хранилища
        file_path = os.path.join(settings.STORAGE_PATH, instance.user.storage_path, instance.unique_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        instance.delete()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            serializer = FileUploadSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                file = serializer.save()
                return Response(
                    FileSerializer(file, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"File upload error: {str(e)}")
            return Response(
                {"error": "File upload failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsFileOwnerOrAdmin]

    def get(self, request, pk):
        file = get_object_or_404(File, pk=pk)

        file.last_download = timezone.now()  # обновление времени
        file.save()

        response = FileResponse(open(file.get_absolute_path(), 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{file.original_name}"'
        return response

class PublicFileDownloadView(APIView):
    permission_classes = []  # Доступ без аутентификации

    def get(self, request, public_link):
        file = get_object_or_404(File, public_link=public_link)
        file_path = os.path.join(settings.STORAGE_PATH, file.user.storage_path, file.unique_name)

        # Обновление даты последнего скачивания
        file.last_download = timezone.now()
        file.save()

        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{file.original_name}"'
        return response
