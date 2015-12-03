from .models import Client
from .models import Project
from django.forms import ModelForm


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
