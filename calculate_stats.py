import json
from fractions import Fraction


def coefficient_calculation(coef):
    k = Fraction(coef).limit_denominator(1000)
    if k.numerator == 0 and k.denominator == 1:
        preliminary = 1000
    else:
        preliminary = k.denominator / k.numerator
    if preliminary < 10:
        return round(preliminary, 1)
    elif preliminary < 50:
        return int(round(preliminary, 0))
    elif preliminary < 250:
        return int(round(preliminary/5, 0)*5)
    elif preliminary < 1000:
        return int(round(preliminary/50, 0)*50)
    elif preliminary >= 1000:
        return 1000


def calculate(entry_id, tokens):
    with open('stats.json', 'r') as file:
        stats = json.load(file)
    stats['total'] += tokens
    stats['entry_stats'][entry_id]['tokens_sum'] += tokens
    for i in range(1, 27):
        stats['entry_stats'][i]['coef'] = stats['entry_stats'][i]['tokens_sum'] / stats['total']
        stats['entry_stats'][i]['current_coef'] = coefficient_calculation(stats['entry_stats'][i]['coef'])
    with open('stats.json', 'w') as file:
        json.dump(stats, file, indent=4)
