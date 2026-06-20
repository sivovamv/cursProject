from .index_views import index, api_test, login_view, logout_view, database_schema, sentry_debug
from .client_views import classes_list, book_class, my_memberships, profile

__all__ = [
    'index', 'api_test', 'login_view', 'logout_view', 'database_schema',
    'sentry_debug', 'classes_list', 'book_class', 'my_memberships', 'profile',
]
