import json
from vk_api.longpoll import VkEventType
import accept_bet
import show_bets
import calculate_stats


def write_msg(user_id, message, vk):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': 0})


def delete_bet(message, user_id, vk):
    # basic syntax check logic
    if not message.isnumeric():
        write_msg(user_id, "Неверный формат! Попробуйте снова.", vk)
        return False
    else:
        bet = int(message)

    user_data = accept_bet.load_data(user_id)

    if bet > len(user_data['bets']) or bet < 1:
        write_msg(user_id, "Неверный номер ставки! Попробуйте снова.", vk)
        return False
    bet -= 1

    # deleting the specified bet by updating general bets data and user's individual data
    calculate_stats.calculate(user_data['bets'][bet]['entry_id'], -user_data['bets'][bet]['tokens'])
    user_data['tokens_available'] += user_data['bets'][bet]['tokens']
    user_data['bets'].pop(bet)
    with open(str(user_id) + '.json', 'w') as file:
        json.dump(user_data, file, indent=4)
    return True


def entry_point(user_id, longpoll, vk):
    if show_bets.entry_point(user_id) == "У вас на данный момент нет никаких ставок.":
        write_msg(user_id, show_bets.entry_point(user_id), vk)
        return
    write_msg(user_id, "Для удаления ставки введите её номер из списка. Для выхода из меню введите 'выход'. " + show_bets.entry_point(user_id), vk)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
            if event.to_me:
                if event.text.lower() == "выход":
                    write_msg(user_id, "Ты, сучка, должна уйти!", vk)
                    return
                if delete_bet(event.text.split()[0], user_id, vk):
                    write_msg(user_id, "Ставка удалена. Вы можете потратить эти 20 тысяч на холодильник!", vk)
                    return
