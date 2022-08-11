import json
import logging

from vk_api.longpoll import VkEventType
from pathlib import Path

from core.db_connection import conn, cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    NO_CATEGORIES_TO_PLACE_BETS_ON,
    SELECT_CATEGORY_TO_PLACE_BETS_ON,
)
from utils import calculate_stats


@menu_decorator()
def get_bet_category_to_bet_on(**kwargs):
    """Method that fetches a list of all ongoing betting categories
    for user to pick for further bet placing."""

    user_id = kwargs.get('user_id')

    # TODO: do we need deadline_date in WHERE block here?
    statement = 'SELECT row_number() OVER (ORDER BY betting_categories.betting_category_id), betting_category_id, ' \
                'c.contest_id, c.name, ct.name, bct.name ' \
                'FROM betting_categories ' \
                'FULL JOIN betting_category_types bct on bct.type_id = betting_categories.category_type ' \
                'LEFT JOIN contests c on c.contest_id = betting_categories.contest_id ' \
                'LEFT JOIN contests_types ct on ct.type_id = c.type ' \
                'WHERE accepts_bets = TRUE;'

    cur.execute(statement)
    categories = cur.fetchall()

    if len(categories) == 0:
        return NO_CATEGORIES_TO_PLACE_BETS_ON, {'terminate_menu': True}

    # TODO
    if len(categories) == 1:
        pass
        # response, extra_info = get_bet_statuses_to_show(invoking_message=str(categories[0][1]))

        # return response, {'terminate_menu': True}

    contests_to_bet_on = tuple(set([category[2] for category in categories]))

    statement = 'SELECT user_id, total, balances.balance_id, contest_id ' \
                'FROM balances ' \
                'LEFT JOIN balances_contests bc on balances.balance_id = bc.balance_id ' \
                f'WHERE user_id = {user_id} ' \
                f'AND contest_id in {contests_to_bet_on};'

    # TODO: handle edge case when a sister contest has been opened after other contests
    #  and user already has balances for them?

    cur.execute(statement)
    balances = cur.fetchall()

    if len(balances) == 0:
        # TODO: consolidate this into a DB-side transaction?

        statement = 'INSERT INTO balances (user_id, total, balance_id) ' \
                    f'VALUES ({user_id}, 100, DEFAULT) ' \
                    f'RETURNING balance_id;'

        cur.execute(statement)
        balance_id = cur.fetchone()[0]
        conn.commit()
        logging.info(f"Created balance {balance_id} for user {user_id}")

        # this will create a balance ONLY for those contests that accept bets

        # for example, if we have a contest whose semifinals have passed
        # and the first time this user checks this menu if after the semifinals
        # he will have a balance created only for the Grand Final
        for contest in contests_to_bet_on:
            statement = 'INSERT INTO balances_contests (balance_id, contest_id) ' \
                        f'VALUES ({balance_id}, {contest});'

            cur.execute(statement)

        conn.commit()
        logging.info(f"Created balance->contest entries for balance {balance_id} and contests {contests_to_bet_on}")

    else:
        balance_id = balances[0][2]

    response = SELECT_CATEGORY_TO_PLACE_BETS_ON

    for category in categories:
        response += f"{category[0]}. {category[3]} {category[4] if category[4] else ''} {category[5]}\n"

    return response, {}


# TODO: picking an entry
# TODO: input validation + db entry
# TODO: check if the time when this bet has been posted it not greater than the deadline

# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


# TODO: merge this function w/ the one below?
def check_tokens(user_id):
    """Checks how many tokens this user has"""
    json_path = str(user_id) + '.json'
    print(f"{json_path} has made a 'check tokens' request")

    if not Path(json_path).exists():
        return 100
    else:
        with open(json_path, 'r') as file:
            user_data = json.load(file)
            return user_data['tokens_available']


def load_data(user_id):
    """Checks whether the user has used this bot before -- if yes, loads their data, otherwise gives them 100 tokens"""
    json_path = str(user_id) + '.json'
    print(f"{json_path} has made a 'load data' request")

    if not Path(json_path).exists():
        return {
                    # TODO: is 'user_id" field even necessary here as we use the filename to keep the user_id?
                    # post-finale update: ok this turned out to be useful when aggregating results, but this issue is still open to debate
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
    """Gets the coefficient of the entry the bet is made on."""
    with open('stats.json', 'r') as stats_f:
        stats = json.load(stats_f)
    return stats['entry_stats'][entry_id]['current_coef']


def bet_processing(user_id, arg_list, tokens_available, vk):
    current_bet = {
        "entry_id": 0,
        "tokens": 0,
        "coefficient": 0,
    }
    user_data = load_data(user_id)

    if arg_list[0].isnumeric() and arg_list[1].isnumeric():
        current_bet["entry_id"] = int(arg_list[0])
        current_bet["tokens"] = int(arg_list[1])

    # simple bet command syntax check
    if current_bet["entry_id"] < 1 or current_bet["entry_id"] > 26:
        write_msg(user_id, "Неверный код страны! Попробуйте ввести запрос снова или введите 'выход' для выхода.", vk)
        return False
    if current_bet["tokens"] < 1 or current_bet["tokens"] > tokens_available:
        write_msg(user_id, "Неверное количество фишек! Попробуйте ввести запрос снова или введите 'выход' для выхода.", vk)
        return False

    current_bet['coefficient'] = get_coefficient(current_bet["entry_id"])

    # updating user's data and saving it into a .json
    print(f"Updating this data: {user_data}")
    user_data['tokens_available'] = tokens_available - current_bet["tokens"]
    user_data['bets'].append(current_bet)
    with open(str(user_id) + '.json', 'w') as file:
        json.dump(user_data, file, indent=4)

    calculate_stats.calculate(current_bet['entry_id'], current_bet['tokens'])

    write_msg(user_id, f"Ставка на заявку {current_bet['entry_id']} в количестве {current_bet['tokens']} фишек с коэффициентом {current_bet['coefficient']} принята! При желании, её можно снять командой 'удалить ставку'.", vk)
    return True


def entry_point(user_id, longpoll, vk):
    tokens_available = check_tokens(user_id)

    if tokens_available == 0:
        write_msg(user_id, "Вы уже использовали все фишки! Вы никогда не были крохобором...", vk)
        return
    else:
        write_msg(user_id, f"Давайте сделаем ставку! У вас есть {tokens_available} фишек.\nЧтобы сделать ставку, введите порядковый номер заявки и количество фишек в формате 'заявка фишки', к примеру, '1 99'.\nВведите 'заявки', если вы хотите увидеть список заявок.", vk)

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
