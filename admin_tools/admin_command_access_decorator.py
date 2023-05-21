import logging

from admin_tools.get_admins_list import get_admins_list
from core.response_strings import NO_PERMISSION_FOR_ADMIN_COMMAND

logging.basicConfig(level=logging.DEBUG)

ADMINS = get_admins_list()


def admin_command_decorator(*args, **kwargs):

    # a friendly reminder -- this part of the decorator
    # is run when it is initialized
    # like, on a `@menu_decorator()` line

    def decorator(menu_step_function):

        # a friendly reminder -- this part of the decorator
        # is run when the decorated function is initialized
        # like, on a `def function_to_dec():` line

        def admin_command_handler(*args, **kwargs) -> tuple[str, dict]:
            """The decorator for validating messsage's regex pattern and calling the target method."""

            user_id = kwargs.get("user_id", 0)

            if user_id not in ADMINS:
                # send a message saying you can't use this command
                logging.info(
                    f"User {user_id} tried to use an admin command, despite having no permission to do so!"
                )

                return NO_PERMISSION_FOR_ADMIN_COMMAND, {"terminate_menu": True}
            else:
                message_to_send, extra_info = menu_step_function(*args, **kwargs)

                logging.info(
                    f"{menu_step_function.__name__} result:\n\n{message_to_send}"
                )

                return message_to_send, extra_info

        return admin_command_handler

    return decorator
