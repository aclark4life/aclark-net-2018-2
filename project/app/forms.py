from .models import Client
from .models import Contact
from .models import Estimate
from .models import Invoice
from .models import Project
from .models import Task
from django.forms import ModelForm


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'


class EstimateForm(ModelForm):
    class Meta:
        model = Estimate
        fields = '__all__'


class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
