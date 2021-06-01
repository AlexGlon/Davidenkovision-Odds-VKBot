import json
from vk_api.longpoll import VkEventType
from pathlib import Path
import calculate_stats

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


def get_coefficient(entry_id):
    with open('stats.json', 'r') as stats_f:
        stats = json.load(stats_f)
    return stats['entry_stats'][entry_id]['current_coef']


def bet_processing(user_id, arg_list, tokens_available, vk):
    # Сообщение от пользователя gets split
    current_bet = {
        "entry_id": 0,
        "tokens": 0,
        "coefficient": 0,
    }
    user_data = load_data(user_id)

    if arg_list[0].isnumeric() and arg_list[1].isnumeric():
        current_bet["entry_id"] = int(arg_list[0])
        current_bet["tokens"] = int(arg_list[1])


    if current_bet["entry_id"] < 1 or current_bet["entry_id"] > 26:
        write_msg(user_id, "Неверный код страны! Попробуйте снова или введите 'выход' для выхода.", vk)
        return False
    if current_bet["tokens"] < 1 or current_bet["tokens"] > tokens_available:
        write_msg(user_id, "Неверное количество фишек! Попробуйте снова или введите 'выход' для выхода.", vk)
        return False

    current_bet['coefficient'] = get_coefficient(current_bet["entry_id"])

    print(user_data)
    user_data['tokens_available'] = tokens_available - current_bet["tokens"]
    user_data['bets'].append(current_bet)
    with open(str(user_id) + '.json', 'w') as file:
        json.dump(user_data, file, indent=4)

    calculate_stats.calculate(current_bet['entry_id'], current_bet['tokens'])

    write_msg(user_id, f"Ставка на заявку {current_bet['entry_id']} в количестве {current_bet['tokens']} фишек с коэффициентом {current_bet['coefficient']} принята! При желании, её можно снять.", vk)
    return True


def entry_point(user_id, longpoll, vk):
    tokens_available = check_tokens(user_id)

    if tokens_available == 0:
        write_msg(user_id, "Вы уже использовали все фишки! Вы никогда не были крахобором...", vk)
        return
    else:
        write_msg(user_id, f"Давайте сделаем ставку! У вас есть {tokens_available} фишек.\nЧтобы сделать ставку, введите порядковый номер заявки и количество фишек в формате '[заявка] [фишки]'.\nВведите 'заявки', если вы хотите вспомнить порядковый номер заявки.", vk)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
            if event.to_me:
                if event.text.lower() == "выход":
                    write_msg(user_id, "Ты, сучка, должна уйти!", vk)
                    return
                if event.text.lower() == "заявки":
                    import show_entries
                    write_msg(user_id, show_entries.entry_iter(), vk)
                    continue
                if bet_processing(user_id, event.text.split(), tokens_available, vk):
                    return
