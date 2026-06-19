from django.shortcuts import render
from ..models import FitnessClass


def schedule_list(request):
    """Расписание занятий"""
    classes = FitnessClass.objects.select_related('trainer__user').all()
    return render(request, 'fitness/schedule_list.html', {'classes': classes})
