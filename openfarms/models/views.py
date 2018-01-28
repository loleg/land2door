from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from .forms import CSVDatasourceForm
from .models import CSVDatasource

class CSVDatasourceView(FormView):
    form_class = CSVDatasourceForm
    template_name = 'csv_upload.html'  # Replace with your template.
    success_url = reverse_lazy('csv:upload')  # Replace with your URL or reverse().

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            instance = CSVDatasource(csv_file=request.FILES['csv_file'])
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
