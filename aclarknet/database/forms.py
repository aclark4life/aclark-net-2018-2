from .models import Client
from .models import Contact
from .models import Estimate
from .models import Invoice
from .models import Project
from .models import Task
from .models import Time
from django import forms


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'


class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = '__all__'


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'


class MailForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'notes', 'project')
