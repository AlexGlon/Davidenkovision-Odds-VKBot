import math
import json


def token_injection_calculation(liked, qualify):
    return int(math.e**((liked+qualify)/100))


def token_injection():
    """Special function used to fill `tokens_sum` fields of an empty entry field in `stats.json` file."""
    with open('stats.json', 'r') as file:
        stats = json.load(file)

    stats['entry_stats'][1]['tokens_sum'] = token_injection_calculation(246, 128)
    stats['entry_stats'][2]['tokens_sum'] = token_injection_calculation(147, 147/1.5)
    stats['entry_stats'][3]['tokens_sum'] = token_injection_calculation(50, 50/1.5)
    stats['entry_stats'][4]['tokens_sum'] = token_injection_calculation(219, 97)
    stats['entry_stats'][5]['tokens_sum'] = token_injection_calculation(175, 87)
    stats['entry_stats'][6]['tokens_sum'] = token_injection_calculation(226, 116)
    stats['entry_stats'][7]['tokens_sum'] = token_injection_calculation(172, 172/1.5)
    stats['entry_stats'][8]['tokens_sum'] = token_injection_calculation(195, 87)
    stats['entry_stats'][9]['tokens_sum'] = token_injection_calculation(136, 72)
    stats['entry_stats'][10]['tokens_sum'] = token_injection_calculation(208, 99)
    stats['entry_stats'][11]['tokens_sum'] = token_injection_calculation(107, 79)
    stats['entry_stats'][12]['tokens_sum'] = token_injection_calculation(240, 118)
    stats['entry_stats'][13]['tokens_sum'] = token_injection_calculation(152, 88)
    stats['entry_stats'][14]['tokens_sum'] = token_injection_calculation(210, 210/1.5)
    stats['entry_stats'][15]['tokens_sum'] = token_injection_calculation(325, 121)
    stats['entry_stats'][16]['tokens_sum'] = token_injection_calculation(114, 74)
    stats['entry_stats'][17]['tokens_sum'] = token_injection_calculation(117, 91)
    stats['entry_stats'][18]['tokens_sum'] = token_injection_calculation(246, 117)
    stats['entry_stats'][19]['tokens_sum'] = token_injection_calculation(483, 149)
    stats['entry_stats'][20]['tokens_sum'] = token_injection_calculation(83, 83/1.5)
    stats['entry_stats'][21]['tokens_sum'] = token_injection_calculation(399, 145)
    stats['entry_stats'][22]['tokens_sum'] = token_injection_calculation(129, 54)
    stats['entry_stats'][23]['tokens_sum'] = token_injection_calculation(283, 126)
    stats['entry_stats'][24]['tokens_sum'] = token_injection_calculation(139, 139/1.5)
    stats['entry_stats'][25]['tokens_sum'] = token_injection_calculation(289, 120)
    stats['entry_stats'][26]['tokens_sum'] = token_injection_calculation(181, 90)

    sum = 0
    for i in range(1, 26):
        sum += stats['entry_stats'][i]['tokens_sum']
    stats['total'] = sum

    with open('stats.json', 'w') as file:
        json.dump(stats, file, indent=4)


token_injection()
