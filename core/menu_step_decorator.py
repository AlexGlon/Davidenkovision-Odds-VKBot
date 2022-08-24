import logging
import re

from core.dialogue_invoker_dicts import DIALOGUE_STEP_INVOKING_PATTERNS
from core.service_strings import EXIT_MENU

logging.basicConfig(level=logging.DEBUG)


def menu_decorator(*args, **kwargs):

    # a friendly reminder -- this part of the decorator
    # is run when it is initialized
    # like, on a `@menu_decorator()` line

    def decorator(menu_step_function):

        # a friendly reminder -- this part of the decorator
        # is run when the decorated function is initialized
        # like, on a `def function_to_dec():` line

        def menu_step_handler(*args, **kwargs) -> tuple[str, dict]:
            """The decorator for validating messsage's regex pattern and calling the target method."""

            invoking_message = kwargs.get("invoking_message", "")

            if re.search(EXIT_MENU, invoking_message.lower()):
                return "", {"terminate_menu": True}

            pattern_to_match = DIALOGUE_STEP_INVOKING_PATTERNS.get(
                menu_step_function.__name__
            )
            result = re.search(pattern_to_match, invoking_message.lower())

            if not result:
                # TODO: implement sending an easter egg message if the syntax is wrong

                logging.info(
                    f"SKIP {invoking_message.lower()} "
                    f"{DIALOGUE_STEP_INVOKING_PATTERNS.get(menu_step_function.__name__)} "
                    f"{DIALOGUE_STEP_INVOKING_PATTERNS}"
                )
                return "flop", {"terminate_menu": True}

            message_to_send, extra_info = menu_step_function(*args, **kwargs)

            # TODO: adding all the necessary data into a special dictionary
            # TODO: `try/except` this block so that if there is an error we can rollback or send the user a message

            logging.info(f"{menu_step_function.__name__} result:\n\n{message_to_send}")

            return message_to_send, extra_info

        return menu_step_handler

    return decorator
