from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from ..models import Membership


def membership_list(request: HttpRequest) -> HttpResponse:
    """
    Страница списка абонементов.

    Args:
        request: HTTP-запрос.
    """
    memberships = Membership.objects.select_related('user', 'tariff_type').all()
    return render(request, 'fitness/membership_list.html', {'memberships': memberships})
