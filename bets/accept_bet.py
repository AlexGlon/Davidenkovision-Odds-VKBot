import json
import logging

from vk_api.longpoll import VkEventType
from pathlib import Path

from core.db_connection import conn, cur
from core.dotenv_variables import COEFFICIENT_OBSCURITY
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    BET_PLACED_SUCCESSFULLY,
    INVALID_CATEGORY_TO_PLACE_BETS_ON,
    INVALID_INPUT_WHILE_PLACING_A_BET,
    NO_CATEGORIES_TO_PLACE_BETS_ON,
    NO_POINTS_TO_SPEND,
    SELECT_CATEGORY_TO_PLACE_BETS_ON,
    SELECT_ENTRY_TO_PLACE_BETS_ON,
)
from flags import country_dict
from utils import calculate_stats
from utils.calculate_stats import coefficient_calculation


@menu_decorator()
def get_bet_category_to_bet_on(**kwargs) -> tuple[str, dict]:
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

    categories_to_bet_on = tuple([category[1] for category in categories])
    categories_to_bet_on_listed_number = tuple([category[0] for category in categories])
    contests_to_bet_on = tuple([category[2] for category in categories])

    statement = 'SELECT user_id, total, balances.balance_id, contest_id ' \
                'FROM balances ' \
                'LEFT JOIN balances_contests bc on balances.balance_id = bc.balance_id ' \
                f'WHERE user_id = {user_id} ' \
                f'AND contest_id in ' \
                f'{contests_to_bet_on if len(categories) > 1 else "(" + str(contests_to_bet_on[0]) + ")"};'

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

        current_points_on_balance = 100

    else:
        balance_id = balances[0][2]
        current_points_on_balance = balances[0][1]

    if current_points_on_balance == 0:
        return NO_POINTS_TO_SPEND, {'terminate_menu': True}

    extra_info = {
        'balance_id': balance_id,
        'categories_listed_number': categories_to_bet_on_listed_number,
        'category_ids': categories_to_bet_on,
        'contest_ids': contests_to_bet_on,
        'current_points_on_balance': current_points_on_balance,
    }

    if len(categories) == 1:
        response, new_extra_info =  get_entry_to_bet_on(
            invoking_message=str(categories[0][1]),
            current_extra_info=extra_info,
            only_one_category=True,
        )
        new_extra_info['skipped_menu_step'] = True

        return response, new_extra_info

    response = SELECT_CATEGORY_TO_PLACE_BETS_ON

    for category in categories:
        response += f"{category[0]}. {category[3]} {category[4] + ' ' if category[4] else ''}{category[5]}\n"

    return response, extra_info


@menu_decorator()
def get_entry_to_bet_on(**kwargs) -> tuple[str, dict]:
    """Method that fetches a list of all entries of the contest that belongs
    to this betting category for user to pick for further bet placing."""

    extra_info = kwargs.get('current_extra_info')
    category_id = int(kwargs.get('invoking_message'))
    only_one_category = kwargs.get('only_one_category')

    valid_categories = extra_info.get('categories_listed_number', ())

    if category_id not in valid_categories and not only_one_category:
        return INVALID_CATEGORY_TO_PLACE_BETS_ON, {'terminate_menu': True}

    if not only_one_category:
        # categories listed number always goes in the ascending format
        db_category_id = extra_info.get('category_ids')[category_id - 1]
    else:
        db_category_id = category_id

    statement = 'SELECT row_number() OVER (ORDER BY entries.entry_id), entries.entry_id, ' \
                'c2.name, year_prefix, artist, title, ' \
                'coefficient ' \
                'FROM entries ' \
                'LEFT JOIN countries c2 on c2.country_id = entries.country_id ' \
                'LEFT JOIN entries_contests ec on entries.entry_id = ec.entry_id ' \
                'LEFT JOIN contests c on c.contest_id = ec.contest_id ' \
                'LEFT JOIN betting_categories bc on c.contest_id = bc.contest_id ' \
                'LEFT JOIN entries_status es on ' \
                '(bc.betting_category_id = es.betting_category_id AND entries.entry_id = es.entry_id) ' \
                f'WHERE bc.betting_category_id = {db_category_id} ' \
                'ORDER BY entries.entry_id;'

    cur.execute(statement)
    entries = cur.fetchall()

    extra_info['coefficients'] = tuple([coefficient_calculation(entry[6]) for entry in entries])
    extra_info['entries_to_bet_on'] = tuple([entry[1] for entry in entries])
    extra_info['entries_to_bet_on_listed_number'] = tuple([entry[0] for entry in entries])
    extra_info['selected_category'] = db_category_id

    if not only_one_category:
        extra_info['selected_contest'] = extra_info.get('contest_ids')[category_id - 1]
    else:
        extra_info['selected_contest'] = extra_info.get('contest_ids')[0]

    response = SELECT_ENTRY_TO_PLACE_BETS_ON

    for entry in entries:
        response += f"{entry[0]}. " \
                    f"{country_dict.get(entry[2])} {entry[2]} {' ' + entry[3] + ' |' if entry[3] else '|'} " \
                    f"{entry[4]} -- {entry[5]}" \
                    f"{' | ' + str(coefficient_calculation(entry[6])) if not COEFFICIENT_OBSCURITY else ''}\n"

    return response, {**extra_info}


@menu_decorator()
def validate_and_accept_incoming_bet(**kwargs) -> tuple[str, dict]:
    """Method that validates the amount of points to bet on an entry
    and chosen entry ID, inserting a DB record after that."""

    extra_info = kwargs.get('current_extra_info')
    # TODO: maybe refactor this so that there is no need to use int() everywhere down the line?
    selected_entry_id, points_to_spend = kwargs.get('invoking_message', '-999 -999').split()

    current_points = extra_info.get('current_points_on_balance', '-999')
    valid_entries = extra_info.get('entries_to_bet_on_listed_number', ())

    if (int(selected_entry_id) not in valid_entries) \
            or (int(points_to_spend) > current_points or int(points_to_spend) <= 0):
        return INVALID_INPUT_WHILE_PLACING_A_BET, {'terminate_menu': True}

    betting_category_id = extra_info.get('selected_category')
    coefficient = extra_info.get('coefficients')[int(selected_entry_id) - 1]
    contest_id = extra_info.get('selected_contest')
    entry_id = extra_info.get('entries_to_bet_on')[int(selected_entry_id) - 1]

    user_id = kwargs.get('user_id')

    statement = 'INSERT INTO bets (user_id, points, coefficient, betting_category_id, contest_id, entry_id) ' \
                f'VALUES ({user_id}, {points_to_spend}, {coefficient}, ' \
                f'{betting_category_id}, {contest_id}, {entry_id});'

    cur.execute(statement)
    conn.commit()
    logging.info(f"Bet has been placed by user {user_id}: "
                 f"betting category {betting_category_id} | entry {entry_id} | points ")
    response = BET_PLACED_SUCCESSFULLY

    return response, {}


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
