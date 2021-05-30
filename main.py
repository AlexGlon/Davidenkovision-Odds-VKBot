from token_vk import token
import vk_api

import emoji

import show_entries

from vk_api.longpoll import VkLongPoll, VkEventType


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})


# Авторизуемся как сообщество
vk = vk_api.VkApi(token=token)

# Работа с сообщениями
longpoll = VkLongPoll(vk)


# Основной цикл
for event in longpoll.listen():

    # Если пришло новое сообщение
    if event.type == VkEventType.MESSAGE_NEW:

        # Если оно имеет метку для меня (то есть бота)
        if event.to_me:

            # Сообщение от пользователя
            request = event.text

            # Каменная логика ответа
            if request == "сучка удали":
                write_msg(event.user_id, "УДАЛИИИИ!")
            elif request == "жыве беларусь!":
                write_msg(event.user_id, show_entries.print_BLR())
            elif request == "ну и хер с тобой, я тоже вызываю!":
                write_msg(event.user_id, show_entries.print_AUS())
            elif request.lower() == "скажи когда":
                write_msg(event.user_id, f" {emoji.emojize(':France: :Faroe_Islands:')} КОГДААААААААААА")
            else:
                write_msg(event.user_id, "Ты чё за ним прячешься?! Ты всё время с кем-нибудь!...")

            print(f"{emoji.emojize(':France: :Faroe_Islands:')} Message sent!")
