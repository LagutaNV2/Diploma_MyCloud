# storage/serializers.py
from rest_framework import serializers
from .models import File
import os
import uuid

class FileSerializer(serializers.ModelSerializer):
    original_name = serializers.CharField(read_only=True)
    size = serializers.IntegerField(read_only=True)
    upload_date = serializers.DateTimeField(read_only=True)
    last_download = serializers.DateTimeField(read_only=True)
    public_link = serializers.UUIDField(read_only=True)

    class Meta:
        model = File
        fields = [
            'id', 'original_name', 'size', 'upload_date',
            'last_download', 'comment', 'public_link'
        ]

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    comment = serializers.CharField(required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        uploaded_file = validated_data['file']

        # Генерация уникального имени файла
        original_name = uploaded_file.name
        file_ext = os.path.splitext(original_name)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"

        # Сохранение файла в хранилище пользователя
        storage_path = user.storage_path
        full_path = os.path.join(storage_path, unique_name)

        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Создание записи в БД
        file = File.objects.create(
            user=user,
            original_name=original_name,
            unique_name=unique_name,
            size=uploaded_file.size,
            comment=validated_data.get('comment', ''),
            public_link=uuid.uuid4()
        )

        return file
