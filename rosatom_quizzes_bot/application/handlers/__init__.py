from .admin import setup_admin_routes
from .quiz import setup_quiz_routes
from .user import setup_user_routes


__all__ = (
    "setup_admin_routes",
    "setup_user_routes",
    "setup_quiz_routes",
)
