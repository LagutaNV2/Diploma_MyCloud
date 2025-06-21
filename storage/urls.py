# storage/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FileViewSet, FileUploadView, FileDownloadView, PublicFileDownloadView

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('files/<uuid:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    path('public/<uuid:public_link>/', PublicFileDownloadView.as_view(), name='public-file-download'),
] + router.urls
