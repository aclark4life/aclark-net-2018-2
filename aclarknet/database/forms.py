from .models import Client
from .models import Company
from .models import Contact
from .models import Contract
from .models import ContractSettings
from .models import Estimate
from .models import File
from .models import Invoice
from .models import Newsletter
from .models import Note
from .models import Profile
from .models import Project
from .models import Proposal
from .models import Report
from .models import Service
from .models import AppSettings
from .models import Task
from .models import Time
from .models import DASHBOARD_CHOICES
from .models import TEMPLATE_CHOICES
from django import forms
from taggit.models import Tag


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        widgets = {
            'bio': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }
        exclude = ('notify', )

    dashboard_choices = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple(attrs={'size': '6'}),
        choices=DASHBOARD_CHOICES)


class AdminTimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = (
            'date',
            'hours',
            'log',
            'client',
            'estimate',
            'invoice',
            'project',
            'user',
            'task',
            'invoiced', )


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'notes': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'
        widgets = {
            'notes': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (  # Exclude uuid instead of include everything else?
            'active',
            'subscribed',
            'first_name',
            'last_name',
            'title',
            'email',
            'mobile_phone',
            'office_phone',
            'fax',
            'address',
            'client',
            'notes', )


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'body': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class ContractSettingsForm(forms.ModelForm):
    class Meta:
        model = ContractSettings
        fields = '__all__'
        widgets = {
            'parties': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'scope_of_work':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'payment_terms':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'timing_of_payment':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'contributor_assignment_agreement':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'authority_to_act':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'termination': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'governing_laws':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'period_of_agreement':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'confidentiality':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'taxes': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'limited_warranty':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
            'complete_agreement':
            forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = (
            'subject',
            'client',
            'project',
            'accepted_date',
            'issue_date',
            'is_sow', )


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = '__all__'


class InvoiceForm(forms.ModelForm):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """

    class Meta:
        model = Invoice
        fields = (
            'subject',
            'client',
            'project',
            'issue_date',
            'last_payment_date', )


class MailForm(forms.Form):
    html = forms.BooleanField(label='HTML', required=False)
    template = forms.ChoiceField(required=False, choices=TEMPLATE_CHOICES)
    message = forms.CharField(widget=forms.Textarea(), required=False)
    subject = forms.CharField(required=False)


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = '__all__'
        widgets = {
            'text': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(
            subscribed=True).exclude(email=None).order_by('first_name'),
        widget=forms.SelectMultiple(attrs={'size': '50'}))


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('active', 'hidden', 'title', 'tags', 'note', 'due_date',
                  'contacts')
        widgets = {
            'note': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': '5'}))

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(active=True).exclude(
            email=None).order_by('first_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={'size': '5'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('rate', )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = '__all__'
        widgets = {
            'body': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'description': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class AppSettingsForm(forms.ModelForm):
    class Meta:
        model = AppSettings
        fields = '__all__'


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'log')
