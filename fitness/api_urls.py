from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets import (
    ClassBookingViewSet,
    FavoriteClassViewSet,
    FitnessClassViewSet,
    MembershipViewSet,
    TrainerViewSet,
)

router = DefaultRouter()
router.register(r'fitness-classes', FitnessClassViewSet, basename='fitnessclass')
router.register(r'class-bookings', ClassBookingViewSet, basename='classbooking')
router.register(r'favorite-classes', FavoriteClassViewSet, basename='favoriteclass')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'trainers', TrainerViewSet, basename='trainer')

urlpatterns = [
    path('api/', include(router.urls)),
]
