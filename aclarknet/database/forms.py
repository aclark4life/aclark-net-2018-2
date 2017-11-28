from .models import Client
from .models import Contact
from .models import Contract
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
from .models import SettingsApp
from .models import SettingsCompany
from .models import SettingsContract
from .models import Task
from .models import Time
from .models import DASHBOARD_CHOICES
from django import forms
from taggit.models import Tag
from django.utils import timezone


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('rate', 'preferred_payment_method', 'bio', 'address',
                  'dashboard_override', 'dashboard_choices', 'icon_size',
                  'notify', 'published')
        widgets = {
            'bio': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }

    dashboard_choices = forms.MultipleChoiceField(
        choices=DASHBOARD_CHOICES,
        label='Dashboard Choices',
        required=False,
        widget=forms.SelectMultiple(attrs={
            'size': '6',
        }))


class AdminTimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = (
            'date',
            'hours',
            'log',
            'estimate',
            'invoice',
            'project',
            'user',
            'task',
            'invoiced',
        )
        widgets = {
            'hours': forms.widgets.NumberInput(attrs={
                'class': 'col-2'
            }),
        }

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'col-2'
        }),
        required=False,
        initial=timezone.now())


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('active', 'first_name', 'last_name', 'email', 'office_phone',
                  'mobile_phone', 'client', 'subscribed')


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = '__all__'
        widgets = {
            'body': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }


class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = (
            'hidden',
            'subject',
            'client',
            'project',
            'accepted_date',
            'issue_date',
            'is_sow',
            'is_to',
            'contacts',
            'user',
        )

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(active=True).exclude(
            email=None).order_by('first_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'size': '5'
        }))


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
            'hidden',
            'subject',
            'po_number',
            'client',
            'project',
            'issue_date',
            'last_payment_date',
        )


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('template_choices', 'contacts', 'subject', 'text')
        widgets = {
            'text': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(subscribed=True).exclude(
            email=None).order_by('first_name'),
        label='Recipients',
        widget=forms.SelectMultiple(attrs={
            'size': '50'
        }),
        required=False)


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('active', 'hidden', 'title', 'tags', 'note', 'due_date',
                  'contacts')
        widgets = {
            'note': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'size': '5'
        }))

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(active=True).exclude(
            email=None).order_by('first_name'),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'size': '5'
        }))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('rate', 'bio', 'address', 'preferred_payment_method',
                  'icon_size')
        widgets = {
            'bio': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('active', 'hidden', 'name', 'start_date', 'end_date',
                  'notes', 'client', 'task', 'team')
        widgets = {
            'notes': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'col-2'
        }),
        required=False,
        initial=timezone.now())

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'col-2'
        }),
        required=False,
        initial=timezone.now())


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = '__all__'
        widgets = {
            'body': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = '__all__'

    invoices = forms.ModelMultipleChoiceField(
        required=False, queryset=Invoice.objects.all().order_by('-issue_date'))


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'description': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }


class SettingsAppForm(forms.ModelForm):
    class Meta:
        model = SettingsApp
        fields = '__all__'


class SettingsCompanyForm(forms.ModelForm):
    class Meta:
        model = SettingsCompany
        fields = '__all__'
        widgets = {
            'notes': forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }


class SettingsContractForm(forms.ModelForm):
    class Meta:
        model = SettingsContract
        fields = '__all__'
        widgets = {
            'parties':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'scope_of_work':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'payment_terms':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'timing_of_payment':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'contributor_assignment_agreement':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'authority_to_act':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'termination':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'governing_laws':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'period_of_agreement':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'confidentiality':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'taxes':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'limited_warranty':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
            'complete_agreement':
            forms.widgets.TextInput(attrs={
                'class': 'tinymce'
            }),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'log')
        widgets = {
            'hours': forms.widgets.NumberInput(attrs={
                'class': 'col-2'
            }),
        }

    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'col-2'
        }),
        required=False,
        initial=timezone.now())
