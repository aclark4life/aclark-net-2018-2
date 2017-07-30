from .utils import gravatar_url
from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from faker import Faker
from multiselectfield import MultiSelectField
from uuid import uuid4
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel
from taggit.managers import TaggableManager

fake = Faker()

# https://github.com/goinnn/django-multiselectfield
COLOR_CHOICES = (
    ('success', 'Success'),
    ('info', 'Info'),
    ('warning', 'Warning'),
    ('danger', 'Danger'), )

DASHBOARD_CHOICES = (
    ('data', 'Data'),
    ('invoices', 'Invoices'),
    ('notes', 'Notes'),
    ('projects', 'Projects'),
    ('times', 'Times'),
    ('totals', 'Totals'), )

EDITOR_CHOICES = (
    ('ckeditor', 'CKEditor'),
    ('tinymce', 'TinyMCE'), )

# Create your models here.


class BaseModel(models.Model):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Client(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    name = models.CharField(max_length=300, blank=True, null=True)
    icon = models.CharField(max_length=25, blank=True, null=True)
    address = models.TextField(blank=True, null=True, default=fake.text)
    description = models.TextField(blank=True, null=True)
    url = models.URLField("Website", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    note = models.ManyToManyField('Note', blank=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Company(SingletonModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    estimate_counter = models.IntegerField(
        "Estimate Counter", blank=True, null=True)
    invoice_counter = models.IntegerField(
        "Invoice Counter", blank=True, null=True)
    currency_symbol = models.CharField(
        "Currency Symbol", default="$", max_length=300, blank=True, null=True)
    note = models.ManyToManyField('Note', blank=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])

    class Meta:
        verbose_name = u'Company'


class Contact(BaseModel):
    """
    Client, First Name, Last Name, Title, Email, Office Phone, Mobile Phone,
    Fax
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    subscribed = models.BooleanField(default=True)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile_phone = PhoneNumberField(blank=True, null=True)
    office_phone = PhoneNumberField(blank=True, null=True)
    fax = PhoneNumberField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    # XXX Should this CharField be a UUIDField instead?
    # https://docs.djangoproject.com/en/1.11/ref/models/fields/#uuidfield
    uuid = models.CharField('UUID', max_length=300, default=uuid4)

    def __str__(self):
        if self.email:
            return ' '.join(
                [self.first_name, self.last_name, '<%s>' % self.email])
        elif self.first_name and self.last_name:
            return ' '.join([self.first_name, self.last_name])
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Contract(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    client = models.ForeignKey(
        'Client', blank=True, null=True, limit_choices_to={'active': True})
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    statement_of_work = models.ForeignKey(
        'Estimate',
        blank=True,
        null=True,
        limit_choices_to={'accepted_date': None})
    task = models.ForeignKey(
        'Task', blank=True, null=True, limit_choices_to={'active': True})
    body = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class ContractSettings(SingletonModel):
    """
    """
    parties = models.TextField(
        'Parties', blank=True, null=True, default=fake.text)
    scope_of_work = models.TextField(
        'Scope of Work', blank=True, null=True, default=fake.text)
    payment_terms = models.TextField(
        'Payment Terms', blank=True, null=True, default=fake.text)
    timing_of_payment = models.TextField(
        'Timing of Payment', blank=True, null=True, default=fake.text)
    contributor_assignment_agreement = models.TextField(
        'Contributor Assignment Agreement',
        blank=True,
        null=True,
        default=fake.text)
    authority_to_act = models.TextField(
        'Authority to Act', blank=True, null=True, default=fake.text)
    termination = models.TextField(
        'Termination', blank=True, null=True, default=fake.text)
    governing_laws = models.TextField(
        'Governing Laws', blank=True, null=True, default=fake.text)
    period_of_agreement = models.TextField(
        'Period of Agreement', blank=True, null=True, default=fake.text)
    confidentiality = models.TextField(
        'Confidentiality', blank=True, null=True, default=fake.text)
    taxes = models.TextField('Taxes', blank=True, null=True, default=fake.text)
    limited_warranty = models.TextField(
        'Limited Warranty', blank=True, null=True, default=fake.text)
    complete_agreement = models.TextField(
        'Complete Agreement', blank=True, null=True, default=fake.text)


# https://docs.djangoproject.com/en/1.11/ref/contrib/gis/model-api/
class Elevation(BaseModel):
    name = models.CharField(max_length=100)
    rast = models.RasterField()


class Estimate(BaseModel):
    """
    Issue Date, Estimate ID, Client, Subject, Estimate Amount, Subtotal,
    Discount, Tax, Tax2, Currency, Accepted Date, Declined Date
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, null=True, default=timezone.now)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    amount = models.DecimalField(
        "Estimate Amount",
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)
    document_id = models.IntegerField("Estimate ID", blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    currency = models.CharField(
        max_length=300,
        blank=True,
        default='United States Dollar - USD',
        null=True, )
    accepted_date = models.DateField(blank=True, null=True)
    declined_date = models.DateField(blank=True, null=True)
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    is_sow = models.BooleanField('Use for Statement of Work?', default=False)

    def __str__(self):
        if self.client and self.document_id:
            return ' '.join(
                [self.client.name, 'Estimate', '#%s' % self.document_id])
        else:
            return 'estimate-%s' % self.document_id


class File(BaseModel):
    """
    """
    name = models.CharField(
        max_length=300, blank=True, null=True, default=fake.text)
    doc = models.FileField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)


class Invoice(BaseModel):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, default=timezone.now, null=True)
    last_payment_date = models.DateField(blank=True, null=True)
    document_id = models.IntegerField("Invoice ID", blank=True, null=True)
    po_number = models.CharField(
        "PO Number", max_length=300, blank=True, null=True)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    amount = models.DecimalField(
        "Invoice Amount",
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)
    paid_amount = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    balance = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    discount = models.IntegerField(blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    currency = models.CharField(
        default="United States Dollar - USD",
        max_length=300,
        blank=True,
        null=True)
    currency_symbol = models.CharField(
        default="$", max_length=300, blank=True, null=True)
    document_type = models.CharField(max_length=300, blank=True, null=True)
    cog = models.DecimalField(
        "Cost of goods",
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)

    def __str__(self):
        return 'invoice-%s' % self.document_id


# https://docs.djangoproject.com/en/1.11/ref/contrib/gis/tutorial/#defining-a-geographic-model
class Location(BaseModel):
    name = models.CharField(max_length=300, default=fake.text)
    area = models.IntegerField(blank=True, null=True)
    pop2005 = models.IntegerField('Population 2005', blank=True, null=True)
    fips = models.CharField('FIPS Code', max_length=2, blank=True, null=True)
    iso2 = models.CharField('2 Digit ISO', max_length=2, blank=True, null=True)
    iso3 = models.CharField('3 Digit ISO', max_length=3, blank=True, null=True)
    un = models.IntegerField('United Nations Code', blank=True, null=True)
    region = models.IntegerField('Region Code', blank=True, null=True)
    subregion = models.IntegerField('Sub-Region Code', blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    mpoly = models.MultiPolygonField(blank=True, null=True)

    def __str__(self):
        return self.name


class Log(BaseModel):
    """
    Log sending of marketing emails and other interesting events.
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    entry = models.CharField(max_length=3000, blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Newsletter(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    text = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    contacts = models.ManyToManyField(
        'Contact',
        blank=True,
        related_name="Contacts",
        limit_choices_to={'subscribed': True})

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Note(BaseModel):
    """
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False)
    due_date = models.DateField("Due", blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    tags = TaggableManager(blank=True, help_text='')
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.title:
            return self.title
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Profile(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    app_admin = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    bio = models.TextField(blank=True, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=300, blank=True, null=True)
    rate = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    unit = models.DecimalField(
        "Unit",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)
    avatar_url = models.URLField(blank=True, null=True)
    notify = models.BooleanField(default=True)
    icon_size = models.CharField(max_length=255, blank=True, null=True)
    page_size = models.PositiveIntegerField(blank=True, null=True)
    dashboard_choices = MultiSelectField(
        choices=DASHBOARD_CHOICES, null=True, blank=True)
    editor_choices = models.CharField(
        max_length=8, choices=EDITOR_CHOICES, null=True, blank=True)
    override_dashboard = models.BooleanField(default=False)
    is_contact = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_avatar_url(self):
        if self.avatar_url is not None:
            return self.avatar_url
        else:
            return gravatar_url(self.user.email)

    def get_username(self):
        if self.username is not None:
            return self.username
        else:
            return self.user.username


class Project(BaseModel):
    """
    Client, Project, Project Code, Start Date, End Date, Project Notes,
    Total Hours, Billable Hours, Billable Amount, Budget, Budget Spent,
    Budget Remaining, Total Costs, Team Costs, Expenses
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    hidden = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    name = models.CharField(
        "Project Name", max_length=300, blank=True, null=True)
    task = models.ForeignKey(
        "Task",
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        limit_choices_to={'profile__active': True})
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    code = models.IntegerField("Project Code", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    billable_hours = models.FloatField(blank=True, null=True)
    billable_amount = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    budget = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    budget_spent = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    budget_remaining = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    total_costs = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    team_costs = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    expenses = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Proposal(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(
        'Client', blank=True, null=True, limit_choices_to={'active': True})
    project = models.ForeignKey(
        "Project",
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    statement_of_work = models.ForeignKey(
        'Estimate',
        blank=True,
        null=True,
        limit_choices_to={'accepted_date': None})
    task = models.ForeignKey(
        'Task', blank=True, null=True, limit_choices_to={'active': True})
    title = models.CharField(max_length=300, blank=True, null=True)
    body = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Report(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=300, blank=True, null=True)
    gross = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    invoices = models.ManyToManyField(
        'Invoice',
        blank=True,
        related_name="Invoices",
        limit_choices_to={'last_payment_date': None})

    def __str__(self):
        return 'report-%s' % self.date


class Service(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    company = models.ForeignKey(Company, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(
        "Font Awesome Icon (without 'fa-')",
        max_length=25,
        blank=True,
        null=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class AppSettings(SingletonModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    icon_size = models.CharField(max_length=255, blank=True, null=True)
    page_size = models.PositiveIntegerField(blank=True, default=1, null=True)
    dashboard_choices = MultiSelectField(
        choices=DASHBOARD_CHOICES, null=True, blank=True)
    auto_hide_notes = models.BooleanField(default=True)
    tags = models.CharField(max_length=255, blank=True, null=True)


class Testimonial(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    company = models.ForeignKey(Company, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, null=True, default=timezone.now)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Task(BaseModel):
    """
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    billable = models.BooleanField(default=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    # https://stackoverflow.com/a/31131029
    color = models.CharField(
        blank=True, choices=COLOR_CHOICES, max_length=7, null=True)
    rate = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    unit = models.DecimalField(
        "Unit",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '-'.join([self._meta.verbose_name, str(self.pk)])


class Time(BaseModel):
    """
    Date, Client, Project, Project Code, Task, Notes, Hours, Billable?,
    Invoiced?, First Name, Last Name, Department, Employee?, Billable
    Rate, Billable Amount, Cost Rate, Cost Amount, Currency,
    External Reference URL
    """
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    billable = models.BooleanField(default=True)
    employee = models.BooleanField(default=True)
    invoiced = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    task = models.ForeignKey(
        Task,
        blank=True,
        null=True,
        limit_choices_to={'active': True}, )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    estimate = models.ForeignKey(
        Estimate, blank=True, null=True, on_delete=models.SET_NULL)
    invoice = models.ForeignKey(
        Invoice, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.now)
    hours = models.DecimalField(
        "Hours",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    department = models.CharField(max_length=300, blank=True, null=True)
    cost_rate = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    cost_amount = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=300, blank=True, null=True)
    external_reference_url = models.URLField(blank=True, null=True)
    project_code = models.IntegerField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    cog = models.DecimalField(
        "Cost of goods",
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2)

    def __str__(self):
        return '-'.join([self._meta.verbose_name, str(self.pk)])

    # https://docs.djangoproject.com/en/1.9/ref/models/instances/#get-absolute-url
    def get_absolute_url(self, hostname):
        return '%s/%s' % (hostname, reverse('entry', args=[str(self.id)]))


# https://docs.djangoproject.com/en/1.11/ref/contrib/gis/model-api/
class Zipcode(BaseModel):
    code = models.CharField(max_length=5)
    poly = models.PolygonField()
