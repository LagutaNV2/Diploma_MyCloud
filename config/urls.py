# config/urls.py
# Настройка главного роутера
from django.contrib import admin
from django.urls import path, include
from users.urls import urlpatterns as users_urls
from storage.urls import urlpatterns as storage_urls
from django.http import JsonResponse

def debug_urls(request):
    from django.urls.resolvers import get_resolver
    resolver = get_resolver()
    return JsonResponse({
        'urls': [str(p) for p in resolver.url_patterns]
    })

def health_check(request):
    return JsonResponse({"status": "OK", "service": "Cloud Storage Backend"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include(users_urls)),
    path('api/storage/', include(storage_urls)),
    path('debug/urls/', debug_urls),  # временный эндпоинт
    path('health/', health_check, name='health-check'),  # Для проверки работоспособности сервиса

    # Для SPA - перенаправляем все остальные запросы на фронтенд
    # Будет создано позже
    # path('', include('frontend.urls')),
]