from .models import Client
from .models import Contact
from .models import Estimate
from .models import Invoice
from .models import Profile
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
        fields = ('issue_date', 'client', 'subject', 'discount',
                  'accepted_date', 'declined_date')


class InvoiceForm(forms.ModelForm):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """

    class Meta:
        model = Invoice
        fields = ('project', 'issue_date', 'invoice_id', 'po_number',
                  'subject')


class MailForm(forms.Form):
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('rate', 'unit')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('active', 'client', 'name', 'code', 'start_date', 'end_date',
                  'task', 'team')


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('active', 'name', 'rate', 'unit')


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'notes', 'client', 'project', 'task')
