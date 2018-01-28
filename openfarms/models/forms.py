from io import TextIOWrapper
from django import forms
from .models import CSVDatasource

class CSVDatasourceForm(forms.ModelForm):
    class Meta:
        model = CSVDatasource
        fields=['title', 'csv_file']
