from aiogram import Dispatcher

from .add_admin import setup_add_admin_routes
from .reset_user import setup_reset_user_routes
from .set_source_url import setup_source_url_routes


__all__ = (
    "setup_admin_routes",
)


def setup_admin_routes(dp: Dispatcher) -> None:
    setup_add_admin_routes(dp)
    setup_reset_user_routes(dp)
    setup_source_url_routes(dp)
