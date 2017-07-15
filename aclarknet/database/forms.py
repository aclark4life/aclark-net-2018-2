from .models import Client
from .models import Company
from .models import Contact
from .models import Contract
from .models import ContractSettings
from .models import Estimate
from .models import Invoice
from .models import Newsletter
from .models import Note
from .models import Profile
from .models import Project
from .models import Proposal
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
        fields = '__all__'


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
        fields = ('document_id', 'issue_date', 'client', 'subject', 'project',
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
            # 'project',
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
        fields = (
            'text',
            'contacts', )
        widgets = {
            'text': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(
            subscribed=True).exclude(email='').order_by('first_name'),
        widget=forms.SelectMultiple(attrs={'size': '50'}))


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('active', 'hidden', 'note')
        # fields = '__all__'
        widgets = {
            'note': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('active', 'app_admin', 'published', 'bio', 'rate',
                  'icon_size', 'page_size', 'override_dashboard',
                  'dashboard_choices')


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('active', 'hidden', 'name', 'start_date', 'end_date',
                  'budget', 'team', 'notes')


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = (
            'client',
            'title',
            'body', )
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
        fields = (
            'active',
            'name',
            'description',
            'icon', )
        widgets = {
            'description': forms.widgets.TextInput(attrs={'class': 'tinymce'}),
        }


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('active', 'name', 'rate', 'unit', 'color')


class TimeForm(forms.ModelForm):
    class Meta:
        model = Time
        fields = ('date', 'hours', 'log')
