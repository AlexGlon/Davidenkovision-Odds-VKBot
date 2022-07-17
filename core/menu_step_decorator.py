import logging

logging.basicConfig(level=logging.DEBUG)


def menu_decorator(*args, **kwargs):

    # a friendly reminder -- this part of the decorator
    # is run when it is initialized
    # like, on a `@menu_decorator()` line

    def decorator(menu_step_function):

        # a friendly reminder -- this part of the decorator
        # is run the decorated function is initialized
        # like, on a `def function_to_dec():` line

        def menu_ster_handler(*args, **kwargs):

            # TODO: verifying invoking message syntax

            message_to_send = menu_step_function(*args, **kwargs)

            # TODO: adding all the necessary data into a special dictionary

            logging.info(f'{menu_step_function.__name__} result:\n\n{message_to_send}')

        return menu_ster_handler

    return decorator
