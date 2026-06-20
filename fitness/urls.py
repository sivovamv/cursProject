from django.urls import path
from .views import (
    index, api_test, login_view, logout_view, database_schema,
    classes_list, book_class, my_memberships, profile, sentry_debug,
)

app_name = 'fitness'

urlpatterns = [
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('classes/', classes_list, name='classes'),
    path('classes/<int:pk>/book/', book_class, name='book_class'),
    path('cabinet/memberships/', my_memberships, name='my_memberships'),
    path('cabinet/profile/', profile, name='profile'),
    path('api-test/', api_test, name='api_test'),
    path('database-schema/', database_schema, name='database_schema'),
    path('sentry-debug/', sentry_debug, name='sentry_debug'),
]
