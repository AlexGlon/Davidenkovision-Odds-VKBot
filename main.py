#!/usr/bin/python3

import datetime
import re

import emoji
import logging
import vk_api

import show_entries
import show_bets
import accept_bet
import delete_bets
import flags
from token_vk import token
from core.db_connection import cur
from core.dicts import FIRST_DIALOGUE_STEPS, NEXT_DIALOGUE_STEP_HANDLERS

from vk_api.longpoll import (
    VkEventType,
    VkLongPoll,
)

# a dictionary that contains information about user's last visited menu
# and temporary information from previous menus

USER_STATES = {}


# TODO: separate this into get/set methods?
def write_msg_and_handle_user_states(user_id: int,
                                     current_step_function) -> dict:
    """Driver method for running the selected menu step function,
    sending the result and updating `USER_STATES` dict as well."""

    message_to_send, new_extra_info = current_step_function(invoking_message=incoming_message)

    write_msg(user_id, message_to_send)

    return {
        'extra_info': new_extra_info
        if not new_extra_info.get('terminate_menu')
        else {},

        'next_step': NEXT_DIALOGUE_STEP_HANDLERS[current_step_function]
        if not new_extra_info.get('terminate_menu')
        else None,

        'last_message_timestamp': datetime.datetime.now()
    }


def write_msg(user_id: int, message: str) -> None:
    """Auxiliary/alias method for sending a message to a VK user."""
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

# this parameter controls whether the bets are in read-only mode (when you can only check your own bets and the bets dashboard)
bets_open = True

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
                    'extra_info': {},
                    'next_step': None,
                    'last_message_timestamp': datetime.datetime.now()
                }

            logging.info(f"New user initialized: {event.user_id}")
            # user's incoming message
            incoming_message = event.text

            # if the user is not in any menu, let's see if his message is amongst those
            # that initiate menu browsing
            if not USER_STATES[event.user_id]['next_step']:

                menu_done_flag = False

                for pattern in FIRST_DIALOGUE_STEPS.keys():
                    if re.search(pattern, incoming_message):

                        USER_STATES[event.user_id] = write_msg_and_handle_user_states(
                            event.user_id,
                            FIRST_DIALOGUE_STEPS[pattern]
                        )

                        menu_done_flag = True
                        break

                # TODO: implement sending an easter egg message if the syntax is wrong
                if not menu_done_flag:
                    pass

            else:
                USER_STATES[event.user_id] = write_msg_and_handle_user_states(
                    event.user_id,
                    USER_STATES[event.user_id]['next_step']
                )

            # =====================================================================================================
            #                                              OLD CODE
            # =====================================================================================================

            # # huge 'if' tree -- maybe it needs to get turned into a separate function
            # if request.lower() == "чего ж ты твaрина!":
            #     if bets_open:
            #         bets_open = False
            #     else:
            #         bets_open = True
            #
            # elif request.lower() == "ставки":
            #     write_msg(event.user_id, show_entries.entry_iter(bet=True))
            # elif request.lower() == "мои ставки":
            #     write_msg(event.user_id, show_bets.entry_point(event.user_id))
            #
            # elif request.lower() == "удалить ставку":
            #     if bets_open:
            #         delete_bets.entry_point(event.user_id, longpoll, vk)
            #     else:
            #         write_msg(event.user_id, "Ставки закрыты и удалить их нельзя!")
            #
            # elif request.lower() == "ставка":
            #     if bets_open:
            #         accept_bet.entry_point(event.user_id, longpoll, vk)
            #     else:
            #         write_msg(event.user_id, "Ставки закрыты и сделать их нельзя!")
            #
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
