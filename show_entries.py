import flags
import json


with open('entries.json', 'r') as file:
    entries = json.load(file)


def entry_iter():
    total_output = ''
    for entry in entries:
        outputF = (lambda x: ' ' if x == None else f" {x} ")(entry['year'])
        output = f"{entry['running_order']} {flags.country_dict[entry['country']]} {entry['country']}"
        output2 = f"{entry['artist']} - {entry['entry']}"
        print(output)
        print(outputF)
        print(output2)

        output = output + outputF + output2
        print(output)

        # flag field uses a special dict defined in flags.py that has all flags.___ commands ready
        # print(entry["running_order"], flags.country_dict[entry['country']],
        #       entry["country"], f"{(lambda x: '' if x == None else x)(entry['year'])}",
        #       entry["artist"], '-', entry["entry"])

        total_output = total_output + output + '\n'

    print(total_output)
    return total_output

def print_BLR():
    return f"2. {flags.Italy} Len - KOGDA"


def print_AUS():
    return f"1. {flags.Australia} Gypsaigne - Deletecolour"