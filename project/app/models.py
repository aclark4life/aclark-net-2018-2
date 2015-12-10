from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from .utils import class_name_pk

# Create your models here.


class Client(models.Model):
    """
    """
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=300, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Contact(models.Model):
    """
    Client, First Name, Last Name, Title, Email, Office Phone, Mobile Phone,
    Fax
    """
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
    """
    project = models.ForeignKey('Project', blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Invoice(models.Model):
    """
    """
    project = models.ForeignKey('Project', blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Task(models.Model):
    """
    """
    name = models.CharField(max_length=300, blank=True, null=True)
    rate = models.DecimalField(blank=True,
                               null=True,
                               max_digits=6,
                               decimal_places=2)
    unit = models.DurationField('Unit', default='01:00', blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Time(models.Model):
    """
    """
    entry = models.DurationField('Time Entry',
                                 default='01:00',
                                 blank=True,
                                 null=True)
    description = models.TextField(blank=True, null=True)

    project = models.ForeignKey('Project', blank=True, null=True)
    task = models.ForeignKey('Task', blank=True, null=True)

    def __unicode__(self):
        return class_name_pk(self)


class Project(models.Model):
    """
    Client, Project, Project Code, Start Date, End Date, Project Notes,
    Total Hours, Billable Hours, Billable Amount, Budget, Budget Spent,
    Budget Remaining, Total Costs, Team Costs, Expenses
    """
    client = models.ForeignKey(Client, blank=True, null=True)
    name = models.CharField(max_length=300, blank=True, null=True)
    code = models.IntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    billable_hours = models.FloatField(blank=True, null=True)
    billable_amount = models.DecimalField(blank=True,
                                          null=True,
                                          max_digits=6,
                                          decimal_places=2)
    budget = models.DecimalField(blank=True,
                                 null=True,
                                 max_digits=6,
                                 decimal_places=2)
    budget_spent = models.DecimalField(blank=True,
                                       null=True,
                                       max_digits=6,
                                       decimal_places=2)
    budget_remaining = models.DecimalField(blank=True,
                                           null=True,
                                           max_digits=6,
                                           decimal_places=2)
    total_costs = models.DecimalField(blank=True,
                                      null=True,
                                      max_digits=6,
                                      decimal_places=2)
    team_costs = models.DecimalField(blank=True,
                                     null=True,
                                     max_digits=6,
                                     decimal_places=2)
    expenses = models.DecimalField(blank=True,
                                   null=True,
                                   max_digits=6,
                                   decimal_places=2)

    def __unicode__(self):
        return self.name
