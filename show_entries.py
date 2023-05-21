import json
import random

import flags
from core.db_connection import cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    INVALID_CONTEST_TO_SHOW_ENTRIES,
    NO_CONTESTS_TO_SHOW_ENTRIES,
    SELECT_CONTEST_TO_SHOW_ENTRIES,
)


@menu_decorator()
def get_contest_to_show_entries(**kwargs):
    """Method that fetches a list of all ongoing contests."""

    query = (
        "SELECT row_number() OVER (ORDER BY contest_id), contest_id, contests.name, ct.name "
        "FROM contests "
        "FULL JOIN contests_types ct "
        "ON ct.type_id = contests.type "
        "WHERE ongoing = TRUE "
        "ORDER BY contest_id;"
    )

    cur.execute(query)
    contests = cur.fetchall()

    if len(contests) == 0:
        return NO_CONTESTS_TO_SHOW_ENTRIES, {"terminate_menu": True}

    if len(contests) == 1:
        response, extra_info = get_entries_to_show(invoking_message=str(contests[0][1]))

        return response, {"terminate_menu": True}

    response = SELECT_CONTEST_TO_SHOW_ENTRIES

    for contest in contests:
        response += f"{contest[0]}. {contest[2]} {contest[3] if contest[3] else ''}\n"

    return response, {}


@menu_decorator()
def get_entries_to_show(**kwargs):
    """Method that fetches a list of all entries from a specified contest."""

    contest_id = kwargs.get("invoking_message")

    query = (
        "SELECT row_number() OVER (ORDER BY entries.entry_id), c.name, year_prefix, artist, title "
        "FROM entries "
        "INNER JOIN entries_contests ec on entries.entry_id = ec.entry_id "
        "INNER JOIN countries c on c.country_id = entries.country_id "
        f"WHERE contest_id = {contest_id} "
        "ORDER BY entries.entry_id;"
    )

    cur.execute(query)
    entries = cur.fetchall()

    if len(entries) == 0:
        return INVALID_CONTEST_TO_SHOW_ENTRIES, {}

    response = ""

    for entry in entries:
        response += (
            f"{entry[0]}. "
            f"{flags.country_dict.get(entry[1])} {entry[1]}{' ' + entry[2] if entry[2] else ''} | "
            f"{entry[3]} -- {entry[4]}\n"
        )

    return response, {}


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


# TODO: rewrite this function
def entry_iter(bet=False):
    with open("entries.json", "r") as file:
        entries = json.load(file)

    total_output = ""
    for entry in entries:
        output_year = (lambda x: " " if x == None else f" {x} ")(entry["year"])
        # flag field uses a special dict defined in flags.py that has all flags.___ commands ready
        output = f"{entry['running_order']}. {flags.country_dict[entry['country']]} {entry['country']}"
        output_entryname = f" | {entry['artist']} — {entry['entry']}"

        if bet:
            with open("stats.json", "r") as stats_f:
                stats = json.load(stats_f)
            entries[entries.index(entry)]["coefficient"] = stats["entry_stats"][
                entry["running_order"]
            ]["current_coef"]

        output = output + output_year + output_entryname
        total_output = total_output + output + "\n"

    if bet:
        bets = sorted(entries, key=lambda i: i["coefficient"])
        total_output = ""
        for entry in bets:
            output_year = (lambda x: "" if x == None else f" {x} ")(entry["year"])
            output = f"{bets.index(entry)+1}. {flags.country_dict[entry['country']]} {entry['country']}"
            output_entryname = (
                f" | {entry['artist']} — {entry['entry']} | {entry['coefficient']}"
            )

            output = output + output_year + output_entryname
            total_output = total_output + output + "\n"

    print(total_output)
    return total_output


# easter egg replies
def print_BLR():
    return f"{flags.Belarus} ты мне скажи когда? КОГДААААААА?????"


def print_AUS():
    return f"{flags.Australia} ну и хер с тобой, я тоже вызываю!"


# undefined command replies
def random_reply():
    # TODO: move these replies into a separate file for easier & quicker editing
    replies = (
        "Ты чё за ним прячешься?! Ты всё время с кем-нибудь!..",
        "Я отвечаю за свои слова, я его сейчас ебану!",
        "До чего ж ты тварина!..",
        "Что ты врёшь, а? Что ты врёшь?!",
        "Пираты, заебали!!!",
        "ДОКУМЕЕЕЕЕНТЫ ПОКАЖИИИИТЕ!",
        "You people are confused!..",
        "Now hey! Hey! I'm ta-a-alking!",
        "Be quiet! I have a question!",
        "Miss who?",
        "Займите своё место, цирк не устраивайте!",
        "Я вам не давала слова! Слова вам не давала!",
        "Перезвоните через полчаса... Сука!",
        "I would never think that... I thought they were really slow...",
        "Я никогда больше в парк одна не пойду!",
        "Нельзя как попало резать лошадь!",
        "Девочки, ну это же стирка, это же порошок!!!",
        "Смотри что ты делаешь, дауниха де-биль-на-ая-я-я!",
        "Отдай муку! Моя мука!",
    )
    return random.choice(replies)
