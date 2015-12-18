from .models import Client
from .models import Contact
from .models import Company
from .models import Contract
from .models import Estimate
from .models import Invoice
from .models import Project
from .models import Task
from .models import Time
from django.contrib import admin
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


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    """


class ContactResource(ImportExportModelResource):
    """
    """

    class Meta:
        exclude = ('client', )
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


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    """


class ProjectResource(ImportExportModelResource):
    """
    """

    class Meta:
        model = Project
        exclude = ('client', )

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):

        if dataset.headers:
            dataset.headers = [str(header).lower().strip()
                               for header in dataset.headers]

        if 'id' not in dataset.headers:
            dataset.headers.append('id')


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    """
    """
    resource_class = ProjectResource


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    """


class TimeResource(ImportExportModelResource):
    """
    """

    class Meta:
        model = Time
        exclude = ('client', 'project', 'task')

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
