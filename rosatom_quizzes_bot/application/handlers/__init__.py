from .admin import setup_admin_routes
from .quiz import setup_quiz_routes
from .start import setup_start_routes


__all__ = (
    "setup_admin_routes",
    "setup_start_routes",
    "setup_quiz_routes",
)
