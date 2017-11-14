from django.db.models import F
from django.db.models import Sum
from decimal import Decimal


def get_total_amount(invoices):
    amount = invoices.aggregate(amount=Sum(F('amount')))['amount']
    return amount


def get_total_cost(projects):
    cost = projects.aggregate(cost=Sum(F('cost')))['cost']
    return cost


def get_total_hours(times, team=None):
    """
    Returns dict of total decimal hours. If team, users' decimal hours too.
    """
    hours = {}
    total_hours = times.aggregate(hours=Sum(F('hours')))['hours']
    if total_hours:
        hours['total'] = total_hours
    else:
        hours['total'] = 0.0
    if team:
        hours['users'] = {}
        for user in team:
            times_user = times.filter(user=user)
            hours_user = times_user.aggregate(hours=Sum(F('hours')))['hours']
            if hours_user:
                hours['users'][user] = hours_user
            else:
                hours['users'][user] = 0.0
    return hours


def set_total_amount(times, estimate=None, invoice=None, project=None):
    """
    Set invoice, estimate and project totals based on task rate
    """
    invoice_amount = 0
    time_entry_amount = 0
    for time_entry in times:
        hours = time_entry.hours
        if time_entry.task:
            rate = time_entry.task.rate
            time_entry_amount = rate * hours
        time_entry.amount = '%.2f' % time_entry_amount
        invoice_amount += time_entry_amount
    if invoice:
        invoice.amount = '%.2f' % invoice_amount
        invoice.save()
    elif estimate:
        estimate.amount = '%.2f' % invoice_amount
        estimate.save()
    elif project:
        cost = 0
        team = project.team.all()
        if team:
            hours = get_total_hours(times, team=team)
            for user in hours['users']:
                rate = user.profile.rate
                cost += rate * Decimal(hours['users'][user])
        project.amount = '%.2f' % invoice_amount
        project.cost = '%.2f' % cost
        project.save()
    return times
