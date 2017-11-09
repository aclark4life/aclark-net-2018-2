from django.db.models import F
from django.db.models import Sum


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
