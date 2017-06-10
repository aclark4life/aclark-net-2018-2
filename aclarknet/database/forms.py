from .models import Client
from .models import Company
from .models import Contact
from .models import Estimate
from .models import Invoice
from .models import Note
from .models import Profile
from .models import Project
from .models import Report
from .models import Service
from .models import Settings
from .models import Task
from .models import Time
from django import forms


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'


class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = ('document_id', 'issue_date', 'client', 'subject',
                  'accepted_date')


class InvoiceForm(forms.ModelForm):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """

    class Meta:
        model = Invoice
        fields = (
            'document_id',
            'po_number',
            'project',
            'issue_date',
            'last_payment_date',
            'subject', )


class MailForm(forms.Form):
    test = forms.BooleanField(required=False)
    subject = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea(), required=False)


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('text', )


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('note', )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('active', 'published', 'bio', 'rate')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('active', 'hidden', 'budget', 'client', 'name', 'notes',
                  'start_date', 'end_date', 'task', 'team')


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('active', 'name', 'rate', 'unit', 'color')


class TimeAdminForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'notes', 'client', 'project', 'task',
                  'user', 'estimate', 'invoice', 'invoiced')


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'notes', 'client', 'project', 'task')
