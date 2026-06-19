from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from .models import (
    ClassBooking,
    FavoriteClass,
    FitnessClass,
    Membership,
    Role,
    TariffType,
    Trainer,
    User,
)
from .serializers import FitnessClassSerializer, MembershipSerializer
from .validators import validate_membership_price, validate_phone_format


class FitnessApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.client_role = Role.objects.create(name='Клиент')
        self.admin_role = Role.objects.create(name='Администратор')
        self.user = User.objects.create(
            full_name='Иван Клиент',
            email='client@example.com',
            phone='+79991234567',
            password_hash='test',
            role=self.client_role,
        )
        self.other_user = User.objects.create(
            full_name='Пётр Другой',
            email='other@example.com',
            phone='+79997654321',
            password_hash='test',
            role=self.client_role,
        )
        self.trainer_user = User.objects.create(
            full_name='Анна Тренер',
            email='trainer@example.com',
            phone='+79990000000',
            password_hash='test',
            role=self.client_role,
        )
        self.trainer = Trainer.objects.create(
            user=self.trainer_user,
            specialization='Йога',
        )
        self.tariff = TariffType.objects.create(
            name='Месячный',
            duration_days=30,
            price=1500,
        )
        self.membership = Membership.objects.create(
            user=self.user,
            tariff_type=self.tariff,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=30),
            status='active',
        )
        self.fitness_class = FitnessClass.objects.create(
            trainer=self.trainer,
            name='Йога утром',
            description='Спокойная тренировка',
            capacity=2,
        )

    def authenticate(self, user=None):
        session = self.client.session
        session['user_id'] = (user or self.user).id
        session.save()

    def test_phone_validation_accepts_russian_phone(self):
        self.assertEqual(validate_phone_format('+7 (999) 123-45-67'), '+79991234567')

    def test_phone_validation_rejects_invalid_phone(self):
        with self.assertRaises(ValidationError):
            validate_phone_format('123')

    def test_membership_price_validation_rejects_low_price(self):
        with self.assertRaises(ValidationError):
            validate_membership_price(100)

    def test_membership_serializer_rejects_wrong_dates(self):
        serializer = MembershipSerializer(data={
            'user': self.user.id,
            'tariff_type': self.tariff.id,
            'start_date': date.today(),
            'end_date': date.today() - timedelta(days=1),
            'status': 'active',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('end_date', serializer.errors)

    def test_fitness_class_serializer_uses_context_for_favorite_flag(self):
        serializer = FitnessClassSerializer(
            self.fitness_class,
            context={'favorite_class_ids': {self.fitness_class.id}},
        )

        self.assertTrue(serializer.data['is_favorite'])

    def test_fitness_classes_api_returns_annotated_fields(self):
        ClassBooking.objects.create(
            user=self.user,
            fitness_class=self.fitness_class,
            status='attended',
        )
        FavoriteClass.objects.create(user=self.user, fitness_class=self.fitness_class)

        response = self.client.get('/api/fitness-classes/')

        self.assertEqual(response.status_code, 200)
        item = response.data['results'][0]
        self.assertEqual(item['bookings_count'], 1)
        self.assertEqual(item['attended_count'], 1)
        self.assertEqual(item['favorite_count'], 1)
        self.assertIn('free_spots', item)

    def test_fitness_class_filter_by_capacity(self):
        FitnessClass.objects.create(
            trainer=self.trainer,
            name='Силовая',
            capacity=30,
        )

        response = self.client.get('/api/fitness-classes/?capacity_min=20')

        self.assertEqual(response.status_code, 200)
        names = {item['name'] for item in response.data['results']}
        self.assertEqual(names, {'Силовая'})

    def test_fitness_class_filter_has_free_spots(self):
        ClassBooking.objects.create(user=self.user, fitness_class=self.fitness_class, status='booked')
        ClassBooking.objects.create(user=self.other_user, fitness_class=self.fitness_class, status='booked')

        response = self.client.get('/api/fitness-classes/?has_free_spots=false')

        self.assertEqual(response.status_code, 200)
        names = {item['name'] for item in response.data['results']}
        self.assertIn('Йога утром', names)

    def test_favorite_create_makes_class_favorite_in_context(self):
        self.authenticate()

        favorite_response = self.client.post('/api/favorite-classes/', {
            'user': self.user.id,
            'fitness_class': self.fitness_class.id,
        })
        classes_response = self.client.get('/api/fitness-classes/')

        self.assertEqual(favorite_response.status_code, 201)
        self.assertTrue(classes_response.data['results'][0]['is_favorite'])

    def test_booking_create_requires_active_membership(self):
        self.authenticate(self.other_user)

        response = self.client.post('/api/class-bookings/', {
            'user': self.other_user.id,
            'fitness_class': self.fitness_class.id,
            'status': 'booked',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('user', response.data)

    def test_booking_create_success_with_active_membership(self):
        self.authenticate()

        response = self.client.post('/api/class-bookings/', {
            'user': self.user.id,
            'fitness_class': self.fitness_class.id,
            'status': 'booked',
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(ClassBooking.objects.count(), 1)

    def test_membership_list_shows_only_current_user_memberships(self):
        Membership.objects.create(
            user=self.other_user,
            tariff_type=self.tariff,
            start_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=30),
            status='active',
        )
        self.authenticate()

        response = self.client.get('/api/memberships/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['user'], self.user.id)

    def test_profile_update_changes_user_data(self):
        session = self.client.session
        session['user_id'] = self.user.id
        session.save()

        response = self.client.post('/cabinet/profile/', {
            'full_name': 'Иван Обновлённый',
            'email': 'new@example.com',
            'phone': '+79991112233',
        })

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.full_name, 'Иван Обновлённый')
        self.assertEqual(self.user.email, 'new@example.com')
