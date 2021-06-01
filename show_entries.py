import flags
import json


with open('entries.json', 'r') as file:
    entries = json.load(file)


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
            output_entryname = f" | {entry['artist']} — {entry['entry']} | {stats['entry_stats'][entry['running_order']]['current_coef']}"

        output = output + output_year + output_entryname
        # print(entry["running_order"], flags.country_dict[entry['country']],
        #       entry["country"], f"{(lambda x: '' if x == None else x)(entry['year'])}",
        #       entry["artist"], '-', entry["entry"])

        total_output = total_output + output + '\n'

    print(total_output)
    return total_output


def print_BLR():
    return f"2. {flags.Belarus} Len - KOGDA"


def print_AUS():
    return f"1. {flags.Australia} Gypsaigne - Deletecolour"