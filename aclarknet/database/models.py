# from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel
from .utils import class_name_pk

# Create your models here.


class Client(models.Model):
    """
    """
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Company(SingletonModel):
    """
    """
    name = models.CharField(max_length=255)
    address = models.TextField()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'Company'


class Contact(models.Model):
    """
    Client, First Name, Last Name, Title, Email, Office Phone, Mobile Phone,
    Fax
    """
    active = models.BooleanField(default=True)
    client = models.ForeignKey(Client, blank=True, null=True)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile_phone = PhoneNumberField(blank=True, null=True)
    office_phone = PhoneNumberField(blank=True, null=True)
    fax = PhoneNumberField(blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Contract(models.Model):
    """
    """

    def __unicode__(self):
        return class_name_pk(self)


class Estimate(models.Model):
    """
    Issue Date, Estimate ID, Client, Subject, Estimate Amount, Subtotal, Discount, Tax,
    Tax2, Currency, Accepted Date, Declined Date
    """
    issue_date = models.DateField(blank=True, null=True)
    estimate_id = models.IntegerField(blank=True, null=True)
    client = models.ForeignKey(Client, blank=True, null=True)
    subject = models.CharField(max_length=300, blank=True, null=True)
    estimate_amount = models.DecimalField(blank=True,
                                          null=True,
                                          max_digits=12,
                                          decimal_places=2)
    subject = models.CharField(max_length=300, blank=True, null=True)
    discount = models.IntegerField(blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    currency = models.CharField(max_length=300, blank=True, null=True)
    accepted_date = models.DateField(blank=True, null=True)
    declined_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Invoice(models.Model):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject, Invoice
    Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2, Currency,
    Currency Symbol, Document Type
    """
    issue_date = models.DateField(blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True)
    invoice_id = models.IntegerField(blank=True, null=True)
    po_number = models.CharField(max_length=300, blank=True, null=True)
    client = models.ForeignKey(Client,
                               blank=True,
                               null=True,
                               limit_choices_to={'active': True}, )
    subject = models.CharField(max_length=300, blank=True, null=True)
    invoice_amount = models.DecimalField(blank=True,
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
    project = models.ForeignKey('Project', blank=True, null=True)
    currency = models.CharField(max_length=300, blank=True, null=True)
    currency_symbol = models.CharField(max_length=300, blank=True, null=True)
    document_type = models.CharField(max_length=300, blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Project(models.Model):
    """
    Client, Project, Project Code, Start Date, End Date, Project Notes,
    Total Hours, Billable Hours, Billable Amount, Budget, Budget Spent,
    Budget Remaining, Total Costs, Team Costs, Expenses
    """
    client = models.ForeignKey(Client,
                               blank=True,
                               null=True,
                               limit_choices_to={'active': True}, )
    name = models.CharField(max_length=300, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
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

    def __unicode__(self):
        return self.name


class Task(models.Model):
    """
    """
    name = models.CharField(max_length=300, blank=True, null=True)
    rate = models.DecimalField(blank=True,
                               null=True,
                               max_digits=12,
                               decimal_places=2)
    unit = models.DurationField('Unit', default='01:00', blank=True, null=True)
    billable = models.BooleanField(default=True)
    active = models.BooleanField(default=True)

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
    client = models.ForeignKey(Client, blank=True, null=True)
    project = models.ForeignKey(Project, blank=True, null=True)
    project_code = models.IntegerField(blank=True, null=True)
    task = models.ForeignKey(Task, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    hours = models.DurationField('Hours',
                                 default='01:00',
                                 blank=True,
                                 null=True)
    billable = models.BooleanField()
    invoiced = models.BooleanField()
    # first_name = models.ForeignKey(User, to_field='first_name',
    # related_name='user_first_name')
    # last_name = models.ForeignKey(User, to_field='last_name')
    department = models.CharField(max_length=300, blank=True, null=True)
    employee = models.BooleanField()
    # billable_amount = models.ForeignKey(Project,
    #                                    blank=True,
    #                                    null=True,
    #                                    to_field='billable_amount',
    #                                    related_name='project_billable_amount')
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

    def __unicode__(self):
        return class_name_pk(self)
