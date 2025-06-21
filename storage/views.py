# storage/views.py
from django.shortcuts import render
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import File
from .serializers import FileSerializer, FileUploadSerializer
from .permissions import IsFileOwnerOrAdmin
import os
from django.conf import settings
from django.utils import timezone

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated, IsFileOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        # Администраторы видят все файлы, обычные пользователи - только свои
        if user.is_admin:
            return File.objects.all()
        return File.objects.filter(user=user)

    def perform_destroy(self, instance):
        # Удаление файла из хранилища
        file_path = os.path.join(settings.STORAGE_PATH, instance.user.storage_path, instance.unique_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        instance.delete()

class FileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            file = serializer.save()
            return Response(FileSerializer(file).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsFileOwnerOrAdmin]

    def get(self, request, pk):
        file = get_object_or_404(File, pk=pk)
        self.check_object_permissions(request, file)

        file_path = os.path.join(settings.STORAGE_PATH, file.user.storage_path, file.unique_name)

        # Обновление даты последнего скачивания
        file.last_download = timezone.now()
        file.save()

        response = FileResponse(open(file_path, 'rb'))
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
