import json

from bets import accept_bet
from core.db_connection import cur
from core.dotenv_variables import COEFFICIENT_OBSCURITY
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    BET_CANCELLATION,
    BET_CREATION_DATE,
    COEFFICIENT,
    HIDDEN_COEFFICIENT,
    NO_BETS_TO_SHOW,
    NO_BETS_TO_SHOW_FOR_CURRENT_CONTESTS,
    POINTS,
    POINTS_RETURNED,
)
from flags import country_dict


@menu_decorator()
def get_current_contests_bets_history(**kwargs):
    """Gets a list of user's bets in all currently ongoing contests."""

    user_id = kwargs.get("user_id")

    # TODO: deprecate `bets.id` since it's not used anywhere down the line
    query = (
        "SELECT row_number() OVER (ORDER BY bets.id), bets.id, c.name, c.ongoing, ct.name, bct.name, "
        "c2.name, e.year_prefix, e.artist, e.title, "
        "bets.points, bets.coefficient, bets.date "
        "FROM bets "
        "LEFT JOIN contests c ON c.contest_id = bets.contest_id "
        "LEFT JOIN contests_types ct on ct.type_id = c.type "
        "LEFT JOIN entries e on e.entry_id = bets.entry_id "
        "LEFT JOIN countries c2 on c2.country_id = e.country_id "
        "LEFT JOIN betting_categories bc on bc.betting_category_id = bets.betting_category_id "
        "LEFT JOIN betting_category_types bct on bct.type_id = bc.category_type "
        "FULL OUTER JOIN bets_cancelled b on bets.id = b.bet_id "
        f"WHERE user_id = {user_id} "
        "AND c.ongoing = TRUE "
        "AND b.bet_id IS NULL "
        "ORDER BY bets.id;"
    )

    cur.execute(query)
    bets = cur.fetchall()

    if len(bets) == 0:
        return NO_BETS_TO_SHOW_FOR_CURRENT_CONTESTS, {}

    response = ""
    # adding this variable here because of SyntaxError
    # that raises with using special symbols in f-strings
    new_line = "\n"

    for bet in bets:
        response += (
            f"{bet[0]}. {BET_CANCELLATION + new_line if bet[10] < 0 else ''}"
            f"{bet[2]} {bet[4] if {bet[4]} else ''}: {bet[5]}\n"
            f"{country_dict.get(bet[6])} {bet[6]}{' ' + bet[7] if bet[7] else ''} | "
            f"{bet[8]} -- {bet[9]}\n"
            f"{POINTS}: {int(bet[10])}\n"
            f"{COEFFICIENT}: {HIDDEN_COEFFICIENT if (COEFFICIENT_OBSCURITY and bet[3]) else bet[11]}\n"
            f"{BET_CREATION_DATE}: {bet[12]}\n\n"
        )

    return response, {}


@menu_decorator()
def get_user_bets_history(**kwargs):
    """Gets a list of user's bets in all contests."""

    user_id = kwargs.get("user_id")

    # TODO: keep `bets.id` for future use (bet cancellation)
    query = (
        "SELECT row_number() OVER (ORDER BY bets.id), bets.id, c.name, c.ongoing, ct.name, bct.name, "
        "c2.name, e.year_prefix, e.artist, e.title, "
        "bets.points, bets.coefficient, bets.date "
        "FROM bets "
        "LEFT JOIN contests c ON c.contest_id = bets.contest_id "
        "LEFT JOIN contests_types ct on ct.type_id = c.type "
        "LEFT JOIN entries e on e.entry_id = bets.entry_id "
        "LEFT JOIN countries c2 on c2.country_id = e.country_id "
        "LEFT JOIN betting_categories bc on bc.betting_category_id = bets.betting_category_id "
        "LEFT JOIN betting_category_types bct on bct.type_id = bc.category_type "
        f"WHERE user_id = {user_id} "
        "ORDER BY bets.id;"
    )

    cur.execute(query)
    bets = cur.fetchall()

    if len(bets) == 0:
        return NO_BETS_TO_SHOW, {}

    response = ""
    # adding this variable here because of SyntaxError
    # that raises with using special symbols in f-strings
    new_line = "\n"

    for bet in bets:
        country = bet[6]
        points = int(bet[10])

        response += (
            f"{bet[0]}. {BET_CANCELLATION + new_line if bet[10] < 0 else ''}"
            f"{bet[2]}{' ' + bet[4] if {bet[4]} else ''}: {bet[5]}\n"
            f"{country_dict.get(country)} {country}{' ' + bet[7] if bet[7] else ''} | "
            f"{bet[8]} -- {bet[9]}\n"
            f"{POINTS if points > 0 else POINTS_RETURNED}: {abs(points)}\n"
            f"{COEFFICIENT}: {HIDDEN_COEFFICIENT if (COEFFICIENT_OBSCURITY and bet[3]) else bet[11]}\n"
            f"{BET_CREATION_DATE}: {bet[12]}\n\n"
        )

    return response, {}


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


def entry_point(user_id):
    user_data = accept_bet.load_data(user_id)
    if not user_data["bets"]:
        return "У вас на данный момент нет никаких ставок."

    with open("entries.json", "r") as file:
        entries = json.load(file)
    response = "Ваши ставки:\n"
    for bet in user_data["bets"]:
        entry = entries[bet["entry_id"] - 1]
        line = f"{user_data['bets'].index(bet)+1}. {country_dict[entry['country']]} {entry['country']}"
        line_year = (lambda x: "" if x == None else f" {x} ")(entry["year"])
        line_entry = f" | {entry['artist']} — {entry['entry']} | (Фишек поставлено: {bet['tokens']}; коэффициент: {bet['coefficient']})\n"
        response += line + line_year + line_entry

    return response
