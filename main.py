#!/usr/bin/python3

import datetime
import json
import logging
import re
import threading

import vk_api
from vk_api.longpoll import VkEventType, VkLongPoll

from core.dicts import (
    FIRST_DIALOGUE_STEPS,
    NEXT_DIALOGUE_STEP_HANDLERS,
    SKIPPING_NEXT_DIALOGUE_STEP_HANDLERS,
)
from core.dotenv_variables import MINUTES_PER_BACKUP, TOKEN
from core.response_strings import (
    WELCOME_MESSAGE,
    get_regular_easter_egg_reply,
    get_welcome_easter_egg_reply,
)

# a dictionary that contains information about user's last visited menu
# and temporary information from previous menus
USER_STATES = {}


def backup_user_states() -> None:
    """Backs up USER_STATES dict once in a certain period of time."""

    threading.Timer(60.0 * MINUTES_PER_BACKUP, backup_user_states).start()

    # preparing data for backup
    USER_STATES_BACKUP = USER_STATES.copy()

    for user, data in USER_STATES_BACKUP.items():
        if callable(data["next_step"]):
            # TODO: figure out how to fix incorrect __name__ representation
            USER_STATES_BACKUP[user]["next_step"] = data["next_step"].__name__
        USER_STATES_BACKUP[user]["last_message_timestamp"] = str(
            data["last_message_timestamp"]
        )

    json_backup = json.dumps(USER_STATES_BACKUP, indent=4)
    backup_date = datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

    with open(f"./user_states_backup/{backup_date}.json", "w") as backup_file:
        backup_file.write(json_backup)
        logging.info(
            f"Backed up USER_STATES in ./user_states_backup/{backup_date}.json file!"
        )


backup_user_states()


# TODO: separate this into get/set methods?
def write_msg_and_handle_user_states(
    user_id: int, incoming_message: str, current_extra_info: dict, current_step_function
) -> dict:
    """Driver method for running the selected menu step function,
    sending the result and updating `USER_STATES` dict as well."""

    message_to_send, new_extra_info = current_step_function(
        invoking_message=incoming_message,
        user_id=user_id,
        current_extra_info=current_extra_info,
    )

    logging.info(f"EXTRA {new_extra_info}")

    if message_to_send:
        write_msg(user_id, message_to_send)

    if new_extra_info.get("terminate_menu"):
        next_step = None
    elif new_extra_info.get("skipped_menu_step"):
        next_step = SKIPPING_NEXT_DIALOGUE_STEP_HANDLERS[current_step_function]
    else:
        next_step = NEXT_DIALOGUE_STEP_HANDLERS[current_step_function]

    return {
        "extra_info": new_extra_info if next_step else {},
        "next_step": next_step,
        "last_message_timestamp": datetime.datetime.now(),
    }


def write_msg(user_id: int, message: str) -> None:
    """Auxiliary/alias method for checking and splitting a message before sending to a VK user."""

    if len(message) > 4096:
        current_first_char_index = 0
        current_last_char_index = 4095

        while True:
            current_split = message[
                current_first_char_index : current_last_char_index + 1
            ]

            if len(current_split) < 4096:
                post_message(user_id, message[current_first_char_index:])
                break

            try:
                last_linebreaks_index = current_split.rindex("\n\n")
            except ValueError:
                last_linebreaks_index = current_last_char_index

            post_message(
                user_id, message[current_first_char_index:last_linebreaks_index]
            )
            current_first_char_index = last_linebreaks_index
            current_last_char_index = last_linebreaks_index + 4096

    else:
        post_message(user_id, message)


def post_message(user_id: int, message: str) -> None:
    """Auxiliary/alias method for sending a message to a VK user."""

    vk.method("messages.send", {"user_id": user_id, "message": message, "random_id": 0})


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=TOKEN)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # initializing user's dict entry
            # if it is the first time they send a message
            if not USER_STATES.get(event.user_id):
                USER_STATES[event.user_id] = {
                    "extra_info": {},
                    "next_step": None,
                    "last_message_timestamp": datetime.datetime.now(),
                }
                logging.info(f"New user initialized: {event.user_id}")
                write_msg(
                    event.user_id, WELCOME_MESSAGE + get_welcome_easter_egg_reply()
                )

            # user's incoming message
            incoming_message = event.text.lower()

            # if the user is not in any menu, let's see if his message is amongst those
            # that initiate menu browsing
            if not USER_STATES[event.user_id]["next_step"]:

                menu_done_flag = False

                for pattern in FIRST_DIALOGUE_STEPS.keys():
                    if re.search(pattern, incoming_message):

                        USER_STATES[event.user_id] = write_msg_and_handle_user_states(
                            event.user_id,
                            incoming_message,
                            USER_STATES[event.user_id]["extra_info"],
                            FIRST_DIALOGUE_STEPS[pattern],
                        )
                        menu_done_flag = True

                        break

                if not menu_done_flag:
                    write_msg(event.user_id, get_regular_easter_egg_reply())

            else:
                USER_STATES[event.user_id] = write_msg_and_handle_user_states(
                    event.user_id,
                    incoming_message,
                    USER_STATES[event.user_id]["extra_info"],
                    USER_STATES[event.user_id]["next_step"],
                )

            # =====================================================================================================
            #                                              OLD CODE
            # =====================================================================================================

            # # easter egg replies
            # elif request.lower() == "скажи когда":
            #     write_msg(event.user_id, f" {flags.Belarus} КОГДААААААААААА")
            # elif request.lower() == "сучка удали":
            #     write_msg(event.user_id, "УДАЛИИИИ!")
            # elif request.lower() == "жыве беларусь!":
            #     write_msg(event.user_id, show_entries.print_BLR())
            # elif request.lower() == "я вызываю милицию":
            #     write_msg(event.user_id, show_entries.print_AUS())
            # # if there's no matching command found
            # else:
            #     write_msg(event.user_id, show_entries.random_reply())

            logging.info(f"Message sent by a bot!")
