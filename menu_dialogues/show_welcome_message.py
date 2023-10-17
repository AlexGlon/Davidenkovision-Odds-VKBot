from core.menu_step_decorator import menu_decorator
from core.response_strings import WELCOME_MESSAGE, get_welcome_easter_egg_reply


@menu_decorator()
def show_welcome_message(**kwargs):
    """Method that shows a list of all available commands."""

    response = WELCOME_MESSAGE + get_welcome_easter_egg_reply()

    return response, {"terminate_menu": True}
