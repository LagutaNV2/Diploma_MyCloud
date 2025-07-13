from rest_framework import serializers
from .models import File
import os
import uuid
from django.conf import settings

class FileSerializer(serializers.ModelSerializer):
    # user = serializers.SerializerMethodField()
    user_id = serializers.PrimaryKeyRelatedField(
        source='user.id', read_only=True
    )
    username = serializers.CharField(
        source='user.username', read_only=True
    )


    class Meta:
        model = File
        fields = '__all__'
        depth = 1  # Включаем связанные объекты


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    comment = serializers.CharField(required=False)

    def create(self, validated_data):
        user = self.context['request'].user
        uploaded_file = validated_data['file']

        if not user.storage_path:
            user.storage_path = f"user_{user.id}/"
            user.save(update_fields=['storage_path'])

        # Генерация уникального имени
        original_name = uploaded_file.name
        file_ext = os.path.splitext(original_name)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"

        # Формирование пути: user_<ID>/<UUID>.<ext>
        file_path = os.path.join(user.storage_path, unique_name)
        full_path = os.path.join(settings.STORAGE_PATH, file_path)

        # Создание директорий
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Сохранение файла
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Создание объекта File
        file = File.objects.create(
            user=user,
            original_name=original_name,
            unique_name=unique_name,
            size=uploaded_file.size,
            comment=validated_data.get('comment', ''),
            public_link=uuid.uuid4(),
            file_path=file_path  # Сохраняем относительный путь
        )

        return file
