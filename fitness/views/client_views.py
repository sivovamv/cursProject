from datetime import date

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from ..decorators import get_session_user, login_required
from ..models import ClassBooking, FitnessClass, Membership, Trainer, User
from ..validators import validate_phone_format


def classes_list(request: HttpRequest) -> HttpResponse:
    """
    Каталог занятий с поиском, фильтрацией и свободными местами.

    Args:
        request: HTTP-запрос с параметрами фильтрации.
    """
    classes = FitnessClass.objects.select_related('trainer__user').annotate(
        active_bookings_count=Count(
            'classbooking',
            filter=Q(classbooking__status__in=('booked', 'attended')),
        ),
    )

    search = request.GET.get('q', '').strip()
    trainer_id = request.GET.get('trainer', '').strip()

    if search:
        classes = classes.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(trainer__user__full_name__icontains=search)
        )
    if trainer_id.isdigit():
        classes = classes.filter(trainer_id=int(trainer_id))

    sort = request.GET.get('sort', 'name')
    if sort == 'spots':
        classes = classes.order_by('-capacity')
    elif sort == 'trainer':
        classes = classes.order_by('trainer__user__full_name', 'name')
    else:
        classes = classes.order_by('name')

    user = get_session_user(request)
    user_booking_class_ids = set()
    has_active_membership = False
    if user:
        user_booking_class_ids = set(
            ClassBooking.objects.filter(
                user=user,
                status='booked',
            ).values_list('fitness_class_id', flat=True)
        )
        has_active_membership = Membership.objects.filter(
            user=user,
            status='active',
            start_date__lte=date.today(),
            end_date__gte=date.today(),
        ).exists()

    class_rows = []
    for fitness_class in classes:
        occupied = fitness_class.active_bookings_count
        class_rows.append({
            'object': fitness_class,
            'free_spots': max(fitness_class.capacity - occupied, 0),
            'occupied': occupied,
            'already_booked': fitness_class.id in user_booking_class_ids,
        })

    return render(request, 'fitness/classes_list.html', {
        'class_rows': class_rows,
        'trainers': Trainer.objects.select_related('user').order_by('user__full_name'),
        'search': search,
        'trainer_id': trainer_id,
        'sort': sort,
        'user': user,
        'has_active_membership': has_active_membership,
    })


@login_required
def book_class(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Запись текущего пользователя на занятие.

    Args:
        request: HTTP-запрос.
        pk: ID занятия.
    """
    fitness_class = get_object_or_404(
        FitnessClass.objects.select_related('trainer__user'),
        pk=pk,
    )
    if request.method != 'POST':
        return redirect('fitness:classes')

    booking = ClassBooking(
        user=request.fitness_user,
        fitness_class=fitness_class,
        status='booked',
    )
    try:
        booking.full_clean()
        booking.save()
        messages.success(request, f'Вы записаны на «{fitness_class.name}».')
    except ValidationError as exc:
        messages.error(request, exc.messages[0] if exc.messages else str(exc))
    except IntegrityError:
        messages.error(request, 'Вы уже записаны на это занятие.')

    return redirect('fitness:classes')


@login_required
def my_memberships(request: HttpRequest) -> HttpResponse:
    """
    Абонементы и история записей текущего пользователя.

    Args:
        request: HTTP-запрос.
    """
    user = request.fitness_user
    memberships = Membership.objects.filter(user=user).select_related('tariff_type').order_by('-start_date')
    bookings = ClassBooking.objects.filter(user=user).select_related(
        'fitness_class',
        'fitness_class__trainer__user',
    ).order_by('-created_at')

    return render(request, 'fitness/my_memberships.html', {
        'memberships': memberships,
        'bookings': bookings,
        'visited_count': bookings.filter(status='attended').count(),
        'user': user,
    })


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """
    Личный кабинет с редактированием ФИО, e-mail и телефона.

    Args:
        request: HTTP-запрос с данными профиля.
    """
    user = request.fitness_user

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()

        if not full_name:
            messages.error(request, 'Укажите ФИО.')
        elif not email:
            messages.error(request, 'Укажите e-mail.')
        elif User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, 'Этот e-mail уже используется.')
        else:
            try:
                if phone:
                    phone = validate_phone_format(phone)
                user.full_name = full_name
                user.email = email
                user.phone = phone
                user.save()
                request.session['user_email'] = user.email
                request.session['user_name'] = user.full_name
                messages.success(request, 'Профиль обновлён.')
                return redirect('fitness:profile')
            except ValidationError as exc:
                message = exc.messages[0] if getattr(exc, 'messages', None) else str(exc)
                messages.error(request, message)

    return render(request, 'fitness/profile.html', {'user': user})
