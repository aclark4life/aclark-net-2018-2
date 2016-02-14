from django.conf import settings
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel
from .utils import class_name_pk

# Create your models here.


class Client(models.Model):
    """
    """
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=300, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Company(SingletonModel):
    """
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    estimate_counter = models.IntegerField("Estimate Counter",
                                           blank=True,
                                           null=True)
    invoice_counter = models.IntegerField("Invoice Counter",
                                          blank=True,
                                          null=True)
    currency_symbol = models.CharField("Currency Symbol",
                                       default="$",
                                       max_length=300,
                                       blank=True,
                                       null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Company'


class Contact(models.Model):
    """
    Client, First Name, Last Name, Title, Email, Office Phone, Mobile Phone,
    Fax
    """
    active = models.BooleanField(default=False)
    client = models.ForeignKey(Client,
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

    def __unicode__(self):
        return class_name_pk(self)


class Estimate(models.Model):
    """
    Issue Date, Estimate ID, Client, Subject, Estimate Amount, Subtotal,
    Discount, Tax, Tax2, Currency, Accepted Date, Declined Date
    """
    issue_date = models.DateField("Issue Date",
                                  blank=True,
                                  null=True,
                                  default=timezone.now)
    client = models.ForeignKey(Client,
                               blank=True,
                               null=True,
                               limit_choices_to={'active': True}, )
    subject = models.CharField(max_length=300, blank=True, null=True)
    amount = models.DecimalField("Estimate Amount",
                                 blank=True,
                                 null=True,
                                 max_digits=12,
                                 decimal_places=2)
    document_id = models.IntegerField("Estimate ID", blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=300,
                                blank=True,
                                default='United States Dollar - USD',
                                null=True, )
    accepted_date = models.DateField(blank=True, null=True)
    declined_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Invoice(models.Model):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """
    issue_date = models.DateField("Issue Date",
                                  blank=True,
                                  default=timezone.now,
                                  null=True)
    last_payment_date = models.DateField(blank=True, null=True)
    document_id = models.IntegerField("Invoice ID", blank=True, null=True)
    po_number = models.CharField("PO Number",
                                 max_length=300,
                                 blank=True,
                                 null=True)
    client = models.ForeignKey(Client,
                               blank=True,
                               null=True,
                               limit_choices_to={'active': True}, )
    subject = models.CharField(max_length=300, blank=True, null=True)
    amount = models.DecimalField("Invoice Amount",
                                 blank=True,
                                 null=True,
                                 max_digits=12,
                                 decimal_places=2)
    paid_amount = models.DecimalField(blank=True,
                                      null=True,
                                      max_digits=12,
                                      decimal_places=2)
    balance = models.DecimalField(blank=True,
                                  null=True,
                                  max_digits=12,
                                  decimal_places=2)
    subtotal = models.DecimalField(blank=True,
                                   null=True,
                                   max_digits=12,
                                   decimal_places=2)
    discount = models.IntegerField(blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    project = models.ForeignKey("Project",
                                blank=True,
                                null=True,
                                limit_choices_to={'active': True}, )
    currency = models.CharField(default="United States Dollar - USD",
                                max_length=300,
                                blank=True,
                                null=True)
    currency_symbol = models.CharField(default="$",
                                       max_length=300,
                                       blank=True,
                                       null=True)
    document_type = models.CharField(max_length=300, blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Profile(models.Model):
    """
    """
    active = models.BooleanField(default=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    rate = models.DecimalField(blank=True,
                               null=True,
                               max_digits=12,
                               decimal_places=2)
    unit = models.DecimalField("Unit",
                               default=1.0,
                               blank=True,
                               null=True,
                               max_digits=12,
                               decimal_places=2)
    def __unicode__(self):
        return self.user.username


class Project(models.Model):
    """
    Client, Project, Project Code, Start Date, End Date, Project Notes,
    Total Hours, Billable Hours, Billable Amount, Budget, Budget Spent,
    Budget Remaining, Total Costs, Team Costs, Expenses
    """
    active = models.BooleanField(default=False)
    client = models.ForeignKey(Client,
                               blank=True,
                               null=True,
                               limit_choices_to={'active': True}, )
    name = models.CharField("Project Name",
                            max_length=300,
                            blank=True,
                            null=True,
                            unique=True)
    code = models.IntegerField("Project Code", blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    billable_hours = models.FloatField(blank=True, null=True)
    billable_amount = models.DecimalField(blank=True,
                                          null=True,
                                          max_digits=12,
                                          decimal_places=2)
    budget = models.DecimalField(blank=True,
                                 null=True,
                                 max_digits=12,
                                 decimal_places=2)
    budget_spent = models.DecimalField(blank=True,
                                       null=True,
                                       max_digits=12,
                                       decimal_places=2)
    budget_remaining = models.DecimalField(blank=True,
                                           null=True,
                                           max_digits=12,
                                           decimal_places=2)
    total_costs = models.DecimalField(blank=True,
                                      null=True,
                                      max_digits=12,
                                      decimal_places=2)
    team_costs = models.DecimalField(blank=True,
                                     null=True,
                                     max_digits=12,
                                     decimal_places=2)
    expenses = models.DecimalField(blank=True,
                                   null=True,
                                   max_digits=12,
                                   decimal_places=2)
    task = models.ForeignKey("Task",
                             blank=True,
                             null=True,
                             limit_choices_to={'active': True}, )
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __unicode__(self):
        return self.name


class Service(models.Model):
    """
    """
    active = models.BooleanField(default=False)
    company = models.ForeignKey(Company,
                                blank=True,
                                null=True)
    name = models.CharField(max_length=300,
                            blank=True,
                            null=True)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Testimonial(models.Model):
    """
    """
    active = models.BooleanField(default=False)
    company = models.ForeignKey(Company,
                                blank=True,
                                null=True)
    name = models.CharField(max_length=300,
                            blank=True,
                            null=True)
    description = models.TextField(blank=True, null=True)
    issue_date = models.DateField("Issue Date",
                                  blank=True,
                                  null=True,
                                  default=timezone.now)

    def __unicode__(self):
        return self.name


class Task(models.Model):
    """
    """
    active = models.BooleanField(default=False)
    billable = models.BooleanField(default=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    rate = models.DecimalField(blank=True,
                               null=True,
                               max_digits=12,
                               decimal_places=2)
    unit = models.DecimalField("Unit",
                               default=1.0,
                               blank=True,
                               null=True,
                               max_digits=12,
                               decimal_places=2)

    def __unicode__(self):
        return self.name


class Time(models.Model):
    """
    Date, Client, Project, Project Code, Task, Notes, Hours, Billable?,
    Invoiced?, First Name, Last Name, Department, Employee?, Billable
    Rate, Billable Amount, Cost Rate, Cost Amount, Currency,
    External Reference URL
    """

    date = models.DateField(default=timezone.now)
    client = models.ForeignKey(Client,
                               blank=True,
                               null=True,
                               limit_choices_to={'active': True}, )
    project = models.ForeignKey(Project,
                                blank=True,
                                null=True,
                                limit_choices_to={'active': True}, )
    project_code = models.IntegerField(blank=True, null=True)
    task = models.ForeignKey(Task,
                             blank=True,
                             null=True,
                             limit_choices_to={'active': True}, )
    notes = models.TextField(blank=True, null=True)
    hours = models.DecimalField("Hours",
                                default=1.0,
                                blank=True,
                                null=True,
                                max_digits=12,
                                decimal_places=2)
    billable = models.BooleanField(default=True)
    invoiced = models.BooleanField(default=False)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    department = models.CharField(max_length=300, blank=True, null=True)
    employee = models.BooleanField(default=True)
    cost_rate = models.DecimalField(blank=True,
                                    null=True,
                                    max_digits=12,
                                    decimal_places=2)
    cost_amount = models.DecimalField(blank=True,
                                      null=True,
                                      max_digits=12,
                                      decimal_places=2)
    currency = models.CharField(max_length=300, blank=True, null=True)
    external_reference_url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    estimate = models.ForeignKey(Estimate,
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
    invoice = models.ForeignKey(Invoice,
                                blank=True,
                                null=True,
                                on_delete=models.SET_NULL)

    def __unicode__(self):
        return class_name_pk(self)
