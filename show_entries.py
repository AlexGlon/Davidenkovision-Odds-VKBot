import json
import random

from core.db_connection import cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import SELECT_CONTEST_TO_SHOW_ENTRIES
import flags


@menu_decorator()
def get_contest_to_show_entries(invoking_message=''):
    """Method that fetches a list of all ongoing contests"""

    statement = 'SELECT contest_id, contests.name, ct.name ' \
                'FROM contests ' \
                'FULL JOIN contests_types ct ' \
                'ON ct.type_id = contests.type ' \
                'WHERE ongoing = true;'

    cur.execute(statement)
    contests = cur.fetchall()

    # TODO: implement skipping everything
    #  if there are no ongoing contests
    if len(contests) == 0:
        pass

    # TODO: implement moving on to showing all entries
    #  if there is just one ongoing contest
    #  so that users skips going through an additional menu
    if len(contests) == 1:
        pass

    response = SELECT_CONTEST_TO_SHOW_ENTRIES

    for contest in contests:
        response += f"{contest[0]}. {contest[1]} {contest[2] if contest[2] else ''}\n"

    return response


@menu_decorator()
def get_entries_to_show(invoking_message='666'):
    contest_id = invoking_message

    statement = 'SELECT entries.entry_id, c.name, year_prefix, artist, title ' \
                'FROM entries ' \
                'INNER JOIN entries_contests ec on entries.entry_id = ec.entry_id ' \
                'INNER JOIN countries c on c.country_id = entries.country_id ' \
                f'WHERE contest_id = {contest_id};'

    cur.execute(statement)
    entries = cur.fetchall()

    response = ''

    for entry in entries:
        response += f"{entry[0]}. " \
                    f"{flags.country_dict.get(entry[1])}{' ' + entry[2] + ' |' if entry[2] else ''} " \
                    f"{entry[3]} -- {entry[4]}\n"

    return response


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


# TODO: rewrite this function
def entry_iter(bet=False):
    with open('entries.json', 'r') as file:
        entries = json.load(file)

    total_output = ''
    for entry in entries:
        output_year = (lambda x: ' ' if x == None else f" {x} ")(entry['year'])
        # flag field uses a special dict defined in flags.py that has all flags.___ commands ready
        output = f"{entry['running_order']}. {flags.country_dict[entry['country']]} {entry['country']}"
        output_entryname = f" | {entry['artist']} — {entry['entry']}"

        if bet:
            with open('stats.json', 'r') as stats_f:
                stats = json.load(stats_f)
            entries[entries.index(entry)]['coefficient'] = stats['entry_stats'][entry['running_order']]['current_coef']

        output = output + output_year + output_entryname
        total_output = total_output + output + '\n'

    if bet:
        bets = sorted(entries, key=lambda i: i['coefficient'])
        total_output = ''
        for entry in bets:
            output_year = (lambda x: '' if x == None else f" {x} ")(entry['year'])
            output = f"{bets.index(entry)+1}. {flags.country_dict[entry['country']]} {entry['country']}"
            output_entryname = f" | {entry['artist']} — {entry['entry']} | {entry['coefficient']}"

            output = output + output_year + output_entryname
            total_output = total_output + output + '\n'

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
    replies = ("Ты чё за ним прячешься?! Ты всё время с кем-нибудь!..",
               "Я отвечаю за свои слова, я его сейчас ебану!",
               "До чего ж ты тварина!..",
               "Что ты врёшь, а? Что ты врёшь?!",
               "Пираты, заебали!!!",
               "ДОКУМЕЕЕЕЕНТЫ ПОКАЖИИИИТЕ!")
    return random.choice(replies)


