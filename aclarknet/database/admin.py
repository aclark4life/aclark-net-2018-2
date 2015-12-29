from .models import Client
from .models import Contact
from .models import Company
from .models import Estimate
from .models import Invoice
from .models import Profile
from .models import Project
from .models import Task
from .models import Time
from .utils import BooleanWidget
from .utils import DecimalWidget
from .utils import UserWidget
from django.contrib import admin
from import_export import fields
from import_export import widgets
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource as ImportExportModelResource
from solo.admin import SingletonModelAdmin

admin.site.register(Company, SingletonModelAdmin)

# Register your models here.


class ClientResource(ImportExportModelResource):
    """
    """

    class Meta:
        model = Client

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = ClientResource


class ContactResource(ImportExportModelResource):
    """
    """
    client = fields.Field(column_name='client',
                          attribute='client',
                          widget=widgets.ForeignKeyWidget(Client, 'name'))

    class Meta:
        model = Contact

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = ContactResource


class EstimateResource(ImportExportModelResource):
    """
    """
    client = fields.Field(column_name='client',
                          attribute='client',
                          widget=widgets.ForeignKeyWidget(Client, 'name'))
    estimate_amount = fields.Field(column_name='estimate_amount',
                                   attribute='estimate_amount',
                                   widget=DecimalWidget())
    subtotal = fields.Field(column_name='subtotal',
                            attribute='subtotal',
                            widget=DecimalWidget())

    class Meta:
        model = Estimate

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Estimate)
class EstimateAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = EstimateResource


class InvoiceResource(ImportExportModelResource):
    """
    """

    client = fields.Field(column_name='client',
                          attribute='client',
                          widget=widgets.ForeignKeyWidget(Client, 'name'))
    amount = fields.Field(column_name='amount',
                          attribute='amount',
                          widget=DecimalWidget())
    paid_amount = fields.Field(column_name='paid_amount',
                               attribute='paid_amount',
                               widget=DecimalWidget())
    subtotal = fields.Field(column_name='subtotal',
                            attribute='subtotal',
                            widget=DecimalWidget())
    balance = fields.Field(column_name='balance',
                           attribute='balance',
                           widget=DecimalWidget())

    class Meta:
        model = Invoice

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = InvoiceResource


class ProjectResource(ImportExportModelResource):
    """
    """
    client = fields.Field(column_name='client',
                          attribute='client',
                          widget=widgets.ForeignKeyWidget(Client, 'name'))
    billable_amount = fields.Field(column_name='billable_amount',
                                   attribute='billable_amount',
                                   widget=DecimalWidget())
    budget = fields.Field(column_name='budget',
                          attribute='budget',
                          widget=DecimalWidget())
    budget_spent = fields.Field(column_name='budget_spent',
                                attribute='budget_spent',
                                widget=DecimalWidget())
    team_costs = fields.Field(column_name='team_costs',
                              attribute='team_costs',
                              widget=DecimalWidget())
    total_costs = fields.Field(column_name='total_costs',
                               attribute='total_costs',
                               widget=DecimalWidget())

    class Meta:
        model = Project
        exclude = ('task', 'team')

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = ProjectResource


class TaskResource(ImportExportModelResource):
    """
    """

    class Meta:
        model = Task
        exclude = ('unit', 'billable', 'active')

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = TaskResource


class TimeResource(ImportExportModelResource):
    """
    """
    billable = fields.Field(column_name='billable',
                            attribute='billable',
                            widget=BooleanWidget())
    client = fields.Field(column_name='client',
                          attribute='client',
                          widget=widgets.ForeignKeyWidget(Client, 'name'))
    invoiced = fields.Field(column_name='invoiced',
                            attribute='invoiced',
                            widget=BooleanWidget())
    project = fields.Field(column_name='project',
                           attribute='project',
                           widget=widgets.ForeignKeyWidget(Project, 'name'))
    task = fields.Field(column_name='task',
                        attribute='task',
                        widget=widgets.ForeignKeyWidget(Task, 'name'))
    user = fields.Field(column_name='user',
                        attribute='user',
                        widget=UserWidget())

    class Meta:
        model = Time

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Time)
class TimeAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = TimeResource
