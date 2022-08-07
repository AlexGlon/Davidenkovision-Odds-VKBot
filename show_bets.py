import json
from flags import country_dict
import accept_bet

from core.db_connection import cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    BET_CANCELLATION,
    BET_CREATION_DATE,
    COEFFICIENT,
    NO_BETS_TO_SHOW_FOR_CURRENT_CONTESTS,
    POINTS,
)


@menu_decorator()
def get_current_contests_bets_history(**kwargs):
    """Gets a list of user's bets in all currently ongoing contests."""

    user_id = kwargs.get('user_id')

    # TODO: keep `bets.id` for future use (bet cancellation)
    statement = 'SELECT row_number() OVER (ORDER BY bets.id), bets.id, c.name, ct.name, bct.name, ' \
                'c2.name, e.year_prefix, e.artist, e.title, ' \
                'bets.points, bets.coefficient, bets.date ' \
                'FROM bets ' \
                'LEFT JOIN contests c ON c.contest_id = bets.contest_id ' \
                'LEFT JOIN contests_types ct on ct.type_id = c.type ' \
                'LEFT JOIN entries e on e.entry_id = bets.entry_id ' \
                'LEFT JOIN countries c2 on c2.country_id = e.country_id ' \
                'LEFT JOIN betting_categories bc on bc.betting_category_id = bets.betting_category_id ' \
                'LEFT JOIN betting_category_types bct on bct.type_id = bc.category_type ' \
                f'WHERE user_id = {user_id} ' \
                'AND c.ongoing = TRUE ' \
                'ORDER BY bets.id;'

    cur.execute(statement)
    bets = cur.fetchall()

    if len(bets) == 0:
        return NO_BETS_TO_SHOW_FOR_CURRENT_CONTESTS, {}

    response = ''
    # adding this variable here because of SyntaxError
    # that raises with using special symbols in f-strings
    new_line = '\n'

    for bet in bets:
        response += f"{bet[0]}. {BET_CANCELLATION + new_line if bet[9] < 0 else ''}" \
                    f"{bet[2]} {bet[3] if {bet[3]} else ''}: {bet[4]}\n" \
                    f"{country_dict.get(bet[5])}{' ' + bet[6] + ' |' if bet[6] else ''} {bet[7]} -- {bet[8]}\n" \
                    f"{POINTS}: {int(bet[9])}\n" \
                    f"{COEFFICIENT}: {bet[10]}\n" \
                    f"{BET_CREATION_DATE}: {bet[11]}\n\n"

    return response, {}


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


def entry_point(user_id):
    user_data = accept_bet.load_data(user_id)
    if not user_data['bets']:
        return "У вас на данный момент нет никаких ставок."

    with open('entries.json', 'r') as file:
        entries = json.load(file)
    response = 'Ваши ставки:\n'
    for bet in user_data['bets']:
        entry = entries[bet['entry_id']-1]
        line = f"{user_data['bets'].index(bet)+1}. {country_dict[entry['country']]} {entry['country']}"
        line_year = (lambda x: '' if x == None else f" {x} ")(entry['year'])
        line_entry = f" | {entry['artist']} — {entry['entry']} | (Фишек поставлено: {bet['tokens']}; коэффициент: {bet['coefficient']})\n"
        response += line + line_year + line_entry

    return response
