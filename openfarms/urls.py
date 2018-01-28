from django.conf.urls import include, url
from .models.views import CSVDatasourceView

urlpatterns = [
    url(r'upload', CSVDatasourceView.as_view(), name='upload')
]
