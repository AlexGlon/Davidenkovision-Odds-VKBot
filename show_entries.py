import flags
import json
import random


with open('entries.json', 'r') as file:
    entries = json.load(file)


# TODO: rewrite this function
def entry_iter(bet=False):
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


