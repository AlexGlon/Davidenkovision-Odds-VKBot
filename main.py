import flags
from token_vk import token
import vk_api

import emoji

import show_entries
import show_bets
import accept_bet
import delete_bets

from vk_api.longpoll import VkLongPoll, VkEventType


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)

bets_open = True

# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text

            # Каменная логика ответа
            if request.lower() == "чего ж ты твaрина!":
                if bets_open:
                    bets_open = False
                else:
                    bets_open = True
            if request.lower() == "сучка удали":
                write_msg(event.user_id, "УДАЛИИИИ!")
            elif request.lower() == "жыве беларусь!":
                write_msg(event.user_id, show_entries.print_BLR())
            elif request.lower() == "я вызываю милицию":
                write_msg(event.user_id, show_entries.print_AUS())
            elif request.lower() == "заявки":
                write_msg(event.user_id, show_entries.entry_iter())
            elif request.lower() == "ставки":
                write_msg(event.user_id, show_entries.entry_iter(bet=True))
            elif request.lower() == "мои ставки":
                write_msg(event.user_id, show_bets.entry_point(event.user_id))
            elif request.lower() == "удалить ставку":
                if bets_open:
                    delete_bets.entry_point(event.user_id, longpoll, vk)
                else:
                    write_msg(event.user_id, "Ставки закрыты и удалить их нельзя!")


            # TODO
            elif request.lower() == "ставка":
                if bets_open:
                    accept_bet.entry_point(event.user_id, longpoll, vk)
                else:
                    write_msg(event.user_id, "Ставки закрыты и сделать их нельзя!")

            elif request.lower() == "скажи когда":
                write_msg(event.user_id, f" {flags.Belarus} КОГДААААААААААА")
            else:
                write_msg(event.user_id, "Ты чё за ним прячешься?! Ты всё время с кем-нибудь!...")

            print(f"{emoji.emojize(':France: :Faroe_Islands:')} Message sent!")
