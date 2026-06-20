from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from ..models import Trainer


def trainer_list(request: HttpRequest) -> HttpResponse:
    """
    Страница списка тренеров.

    Args:
        request: HTTP-запрос.
    """
    trainers = Trainer.objects.select_related('user').all()
    return render(request, 'fitness/trainer_list.html', {'trainers': trainers})
