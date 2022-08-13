import json
from vk_api.longpoll import VkEventType

import bets.show_bets as show_bets
from core.dotenv_variables import COEFFICIENT_OBSCURITY
from flags import country_dict
from utils import calculate_stats
from bets import accept_bet

from core.db_connection import cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    NO_BETS_TO_CANCEL,
    SELECT_BET_TO_CANCEL, POINTS, HIDDEN_COEFFICIENT, COEFFICIENT, BET_CREATION_DATE,
)


@menu_decorator()
def get_bets_eligible_for_deletion(**kwargs) -> tuple[str, dict]:
    """Gets a list of user's bet from the current contests
    that they can cancel."""

    user_id = kwargs.get('user_id')

    query = 'SELECT row_number() OVER (ORDER BY bets.id), ' \
            'bets.id, points, coefficient, ' \
            'bets.betting_category_id, bets.contest_id, bets.entry_id, ' \
            'contests.name, ct.name, bct.name, ' \
            'c.name, e.year_prefix, e.artist, e.title, ' \
            'bets.date ' \
            'FROM bets ' \
            'LEFT JOIN contests on bets.contest_id = contests.contest_id ' \
            'LEFT JOIN contests_types ct on ct.type_id = contests.type ' \
            'LEFT JOIN betting_categories bc on bc.betting_category_id = bets.betting_category_id ' \
            'LEFT JOIN betting_category_types bct on bct.type_id = bc.category_type ' \
            'LEFT JOIN entries e on e.entry_id = bets.entry_id ' \
            'LEFT JOIN countries c on c.country_id = e.country_id ' \
            'FULL OUTER JOIN bets_cancelled b on bets.id = b.bet_id ' \
            f'WHERE user_id = {user_id} ' \
            'AND b.bet_id IS NULL ' \
            'AND bc.accepts_bets = TRUE;'

    cur.execute(query)
    bets = cur.fetchall()

    if len(bets) == 0:
        return NO_BETS_TO_CANCEL, {'terminate_menu': True}

    # TODO: handle len(bets) == 1

    extra_info = {
        'bet_listed_number': [],
        'bet_id': [],
        'points': [],
        'coefficients': [],
        'betting_category_ids': [],
        'contest_ids': [],
        'entry_ids': [],
        'entries': [],
    }
    response = SELECT_BET_TO_CANCEL

    for bet in bets:
        extra_info['bet_listed_number'].append(bet[0])
        extra_info['bet_id'].append(bet[1])
        extra_info['points'].append(bet[2])
        extra_info['coefficients'].append(bet[3])
        extra_info['betting_category_ids'].append(bet[4])
        extra_info['contest_ids'].append(bet[5])
        extra_info['entry_ids'].append(bet[6])

        entry_info = {
            'contest_name': bet[7],
            'contest_type': bet[8],
            'betting_category': bet[9],
            'country': bet[10],
            'year_prefix': bet[11],
            'artist': bet[12],
            'title': bet[13],
        }
        extra_info['entries'].append(entry_info)

        response += f"{bet[0]}. {entry_info['contest_name']}" \
                    f"{' ' + entry_info['contest_type'] if entry_info['contest_type'] else ''} " \
                    f"{entry_info['betting_category']}\n" \
                    f"{country_dict.get(entry_info['country'])} {entry_info['country']}" \
                    f"{' ' + entry_info['year_prefix'] + ' |' if entry_info['year_prefix'] else ' |'} " \
                    f"{entry_info['artist']} -- {entry_info['title']}\n" \
                    f"{POINTS}: {int(bet[2])}\n" \
                    f"{COEFFICIENT}: {HIDDEN_COEFFICIENT if COEFFICIENT_OBSCURITY else bet[3]}\n" \
                    f"{BET_CREATION_DATE}: {bet[14]}\n\n"

    extra_info['bet_listed_number'] = tuple(extra_info['bet_listed_number'])
    extra_info['bet_id'] = tuple(extra_info['bet_id'])
    extra_info['points'] = tuple(extra_info['points'])
    extra_info['coefficients'] = tuple(extra_info['coefficients'])
    extra_info['betting_category_ids'] = tuple(extra_info['betting_category_ids'])
    extra_info['contest_ids'] = tuple(extra_info['contest_ids'])
    extra_info['entry_ids'] = tuple(extra_info['entry_ids'])
    extra_info['entries'] = tuple(extra_info['entries'])

    return response, extra_info


@menu_decorator()
def get_bet_cancellation_confirmation(**kwargs) -> tuple[str, dict]:
    return '', {}


@menu_decorator()
def cancel_selected_bet(**kwargs) -> tuple[str, dict]:
    return '', {}


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


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
