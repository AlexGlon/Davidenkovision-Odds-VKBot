import json
import logging

from vk_api.longpoll import VkEventType

import bets.show_bets as show_bets
from bets import accept_bet
from core.db_connection import conn, cur
from core.dotenv_variables import COEFFICIENT_OBSCURITY
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    BET_CANCELLATION_ABORTED,
    BET_CANCELLATION_SUCCESS,
    BET_CREATION_DATE,
    BETTING_CATEGORY_CLOSED_FOR_CANCELLING_BETS,
    COEFFICIENT,
    CONFIRM_BET_CANCELLATION,
    HIDDEN_COEFFICIENT,
    INVALID_BET_TO_CANCEL_NUMBER,
    NO_BETS_TO_CANCEL,
    POINTS,
    SELECT_BET_TO_CANCEL,
)
from flags import country_dict
from utils import calculate_stats


@menu_decorator()
def get_bets_eligible_for_deletion(**kwargs) -> tuple[str, dict]:
    """Gets a list of user's bet from the current contests
    that they can cancel."""

    user_id = kwargs.get("user_id")

    query = (
        "SELECT row_number() OVER (ORDER BY bets.id), "
        "bets.id, points, coefficient, "
        "bets.betting_category_id, bets.contest_id, bets.entry_id, "
        "contests.name, ct.name, bct.name, "
        "c.name, e.year_prefix, e.artist, e.title, "
        "bets.date "
        "FROM bets "
        "LEFT JOIN contests on bets.contest_id = contests.contest_id "
        "LEFT JOIN contests_types ct on ct.type_id = contests.type "
        "LEFT JOIN betting_categories bc on bc.betting_category_id = bets.betting_category_id "
        "LEFT JOIN betting_category_types bct on bct.type_id = bc.category_type "
        "LEFT JOIN entries e on e.entry_id = bets.entry_id "
        "LEFT JOIN countries c on c.country_id = e.country_id "
        "FULL OUTER JOIN bets_cancelled b on bets.id = b.bet_id "
        f"WHERE user_id = {user_id} "
        "AND b.bet_id IS NULL "
        "AND bc.accepts_bets = TRUE;"
    )

    cur.execute(query)
    bets = cur.fetchall()

    if len(bets) == 0:
        return NO_BETS_TO_CANCEL, {"terminate_menu": True}

    extra_info = {
        "bet_listed_numbers": [],
        "bet_ids": [],
        "points": [],
        "coefficients": [],
        "betting_category_ids": [],
        "contest_ids": [],
        "entry_ids": [],
        "entries": [],
        "bet_creation_dates": [],
    }
    response = SELECT_BET_TO_CANCEL

    for bet in bets:
        extra_info["bet_listed_numbers"].append(bet[0])
        extra_info["bet_ids"].append(bet[1])
        extra_info["points"].append(bet[2])
        extra_info["coefficients"].append(bet[3])
        extra_info["betting_category_ids"].append(bet[4])
        extra_info["contest_ids"].append(bet[5])
        extra_info["entry_ids"].append(bet[6])
        extra_info["bet_creation_dates"].append(bet[14])

        entry_info = {
            "contest_name": bet[7],
            "contest_type": bet[8],
            "betting_category": bet[9],
            "country": bet[10],
            "year_prefix": bet[11],
            "artist": bet[12],
            "title": bet[13],
        }
        extra_info["entries"].append(entry_info)

        response += (
            f"{bet[0]}. {entry_info['contest_name']}"
            f"{' ' + entry_info['contest_type'] if entry_info['contest_type'] else ''} "
            f"{entry_info['betting_category']}\n"
            f"{country_dict.get(entry_info['country'])} {entry_info['country']}"
            f"{' ' + entry_info['year_prefix'] if entry_info['year_prefix'] else ''} | "
            f"{entry_info['artist']} -- {entry_info['title']}\n"
            f"{POINTS}: {int(bet[2])}\n"
            f"{COEFFICIENT}: {HIDDEN_COEFFICIENT if COEFFICIENT_OBSCURITY else bet[3]}\n"
            f"{BET_CREATION_DATE}: {bet[14]} UTC\n\n"
        )

    extra_info["bet_listed_numbers"] = tuple(extra_info["bet_listed_numbers"])
    extra_info["bet_ids"] = tuple(extra_info["bet_ids"])
    extra_info["points"] = tuple(extra_info["points"])
    extra_info["coefficients"] = tuple(extra_info["coefficients"])
    extra_info["betting_category_ids"] = tuple(extra_info["betting_category_ids"])
    extra_info["contest_ids"] = tuple(extra_info["contest_ids"])
    extra_info["entry_ids"] = tuple(extra_info["entry_ids"])
    extra_info["entries"] = tuple(extra_info["entries"])
    extra_info["bet_creation_dates"] = tuple(extra_info["bet_creation_dates"])

    if len(bets) == 1:
        response, new_extra_info = get_bet_cancellation_confirmation(
            invoking_message="1",
            current_extra_info=extra_info,
            only_one_bet=True,
        )
        new_extra_info["skipped_menu_step"] = True

        return response, new_extra_info

    return response, extra_info


@menu_decorator()
def get_bet_cancellation_confirmation(**kwargs) -> tuple[str, dict]:
    """Validates user's bet to cancel choice
    and asks for user's confirmation."""

    extra_info = kwargs.get("current_extra_info")
    only_one_bet = kwargs.get("only_one_bet")
    selected_bet = int(kwargs.get("invoking_message"))

    existing_bets = extra_info.get("bet_listed_numbers")

    if selected_bet not in existing_bets and not only_one_bet:
        return INVALID_BET_TO_CANCEL_NUMBER, {"terminate_menu": True}

    extra_info["selected_bet_listed_number"] = selected_bet

    bet_creation_date = extra_info.get("bet_creation_dates")[selected_bet - 1]
    coefficient = extra_info.get("coefficients")[selected_bet - 1]
    entry_info = extra_info.get("entries")[selected_bet - 1]
    points = extra_info.get("points")[selected_bet - 1]

    response = CONFIRM_BET_CANCELLATION.format(id=selected_bet)

    response += (
        f"{selected_bet}. {entry_info['contest_name']}"
        f"{' ' + entry_info['contest_type'] if entry_info['contest_type'] else ''} "
        f"{entry_info['betting_category']}\n"
        f"{country_dict.get(entry_info['country'])} {entry_info['country']}"
        f"{' ' + entry_info['year_prefix'] if entry_info['year_prefix'] else ''} | "
        f"{entry_info['artist']} -- {entry_info['title']}\n"
        f"{POINTS}: {int(points)}\n"
        f"{COEFFICIENT}: {HIDDEN_COEFFICIENT if COEFFICIENT_OBSCURITY else coefficient}\n"
        f"{BET_CREATION_DATE}: {bet_creation_date} UTC\n\n"
    )

    return response, extra_info


@menu_decorator()
def cancel_selected_bet(**kwargs) -> tuple[str, dict]:
    """Validates user's confirmation choice
    and cancels the bet (if a confirmation is given)."""

    confirmation_message = int(kwargs.get("invoking_message"))
    extra_info = kwargs.get("current_extra_info")
    user_id = kwargs.get("user_id")

    selected_bet_listed_number = extra_info.get("selected_bet_listed_number")

    if confirmation_message != selected_bet_listed_number:
        return BET_CANCELLATION_ABORTED, {"terminate_menu": True}

    # add a cancelled bet to `bets` table

    bet_to_cancel_id = extra_info.get("bet_ids")[confirmation_message - 1]
    betting_category_id = extra_info.get("betting_category_ids")[
        confirmation_message - 1
    ]
    coefficient = extra_info.get("coefficients")[confirmation_message - 1]
    contest_id = extra_info.get("contest_ids")[confirmation_message - 1]
    entry_id = extra_info.get("entry_ids")[confirmation_message - 1]
    points = -extra_info.get("points")[confirmation_message - 1]

    # checking if this betting category still accepts bets
    query = (
        "SELECT accepts_bets "
        "FROM betting_categories "
        f"WHERE betting_category_id = {betting_category_id};"
    )

    cur.execute(query)

    if not bool(cur.fetchall()[0][0]):
        return BETTING_CATEGORY_CLOSED_FOR_CANCELLING_BETS, {"terminate_menu": True}

    query = (
        "INSERT INTO bets (user_id, points, coefficient, betting_category_id, contest_id, entry_id) "
        f"VALUES ({user_id}, {points}, {coefficient}, "
        f"{betting_category_id}, {contest_id}, {entry_id}) "
        f"RETURNING id;"
    )

    cur.execute(query)

    # add entries for cancelled bets into `bets_cancelled` table

    freshly_cancelled_bet_id = cur.fetchone()[0]

    query = (
        "INSERT INTO bets_cancelled (bet_id) "
        f"VALUES ({bet_to_cancel_id}), ({freshly_cancelled_bet_id});"
    )

    cur.execute(query)

    conn.commit()
    logging.info(
        f"Bet {bet_to_cancel_id} has been canceled by user {user_id}: "
        f"betting category {betting_category_id} | entry {entry_id} | {-points} points "
    )

    return BET_CANCELLATION_SUCCESS, {}


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


def write_msg(user_id, message, vk):
    vk.method("messages.send", {"user_id": user_id, "message": message, "random_id": 0})


def delete_bet(message, user_id, vk):
    # basic syntax check logic
    if not message.isnumeric():
        write_msg(user_id, "Неверный формат! Попробуйте снова.", vk)
        return False
    else:
        bet = int(message)

    user_data = accept_bet.load_data(user_id)

    if bet > len(user_data["bets"]) or bet < 1:
        write_msg(user_id, "Неверный номер ставки! Попробуйте снова.", vk)
        return False
    bet -= 1

    # deleting the specified bet by updating general bets data and user's individual data
    calculate_stats.calculate(
        user_data["bets"][bet]["entry_id"], -user_data["bets"][bet]["tokens"]
    )
    user_data["tokens_available"] += user_data["bets"][bet]["tokens"]
    user_data["bets"].pop(bet)
    with open(str(user_id) + ".json", "w") as file:
        json.dump(user_data, file, indent=4)
    return True


def entry_point(user_id, longpoll, vk):
    if show_bets.entry_point(user_id) == "У вас на данный момент нет никаких ставок.":
        write_msg(user_id, show_bets.entry_point(user_id), vk)
        return
    write_msg(
        user_id,
        "Для удаления ставки введите её номер из списка. Для выхода из меню введите 'выход'. "
        + show_bets.entry_point(user_id),
        vk,
    )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.user_id == user_id:
            if event.to_me:
                if event.text.lower() == "выход":
                    write_msg(user_id, "Ты, сучка, должна уйти!", vk)
                    return
                if delete_bet(event.text.split()[0], user_id, vk):
                    write_msg(
                        user_id,
                        "Ставка удалена. Вы можете потратить эти 20 тысяч на холодильник!",
                        vk,
                    )
                    return
