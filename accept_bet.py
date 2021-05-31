import json
from vk_api.longpoll import VkEventType


from pathlib import Path

# TODO: user sends an entry code and how much tokens he wants to bet


# first of all we check whether a fitting json file exists
def check_tokens(user_id):
    json_path = str(user_id) + '.json'
    print(json_path)

    if not Path(json_path).exists():
        return 100
    else:
        with open(json_path, 'r') as file:
            user_data = json.load(file)
            return user_data['tokens_available']


def load_data(user_id):
    json_path = str(user_id) + '.json'
    print(json_path)

    if not Path(json_path).exists():
        return {
                    # TODO: is 'user_id" field even necessary here as we use the filename to keep the user_id?
                    "user_id": user_id,
                    "tokens_available": 100,
                    "bets": []
                }
    else:
        with open(json_path, 'r') as file:
            return json.load(file)


def write_msg(user_id, message, vk):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})



def entry_point(user_id, longpoll, vk):

    tokens_available = check_tokens(user_id)

    if tokens_available == 0:
        write_msg(user_id, "Вы уже использовали все фишки! Вы никогда не были крахобором...", vk)
        return
    else:
        write_msg(user_id, f"Давайте сделаем ставку! У вас есть {tokens_available} фишек.\nЧтобы сделать ставку, введите порядковый номер заявки и количество фишек в формате '[заявка] [фишки]'.", vk)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
            if event.to_me:

                # Сообщение от пользователя gets split
                arg_list = event.text.split()
                current_bet = {
                    "country_id": 0,
                    "tokens": 0
                }
                user_data = load_data(user_id)

                if arg_list[0].isnumeric() and arg_list[1].isnumeric():
                    current_bet["country_id"] = int(arg_list[0])
                    current_bet["tokens"] = int(arg_list[1])

                if current_bet["country_id"] < 1 or current_bet["country_id"] > 26:
                    write_msg(user_id, "Неверный код страны!", vk)
                    return
                if current_bet["tokens"] < 1 or current_bet["tokens"] > tokens_available:
                    write_msg(user_id, "Неверное количество фишек!", vk)
                    return

                print(user_data)
                user_data['tokens_available'] = tokens_available - current_bet["tokens"]
                user_data['bets'].append(current_bet)

                with open(str(user_id) + '.json', 'w') as file:
                    json.dump(user_data, file, indent=4)

                write_msg(user_id, f"Ставка на заявку {current_bet['country_id']} в количестве {current_bet['tokens']} фишек с коэффициентом {'__'} принята! При желании, её можно снять.", vk)
                return
