from .models import Client
from .models import Contact
from .models import Contract
from .models import Estimate
from .models import Invoice
from .models import Project
from .models import Task
from django.contrib import admin

# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    """
