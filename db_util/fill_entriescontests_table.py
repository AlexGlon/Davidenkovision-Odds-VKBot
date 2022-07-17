import math

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    # database="davidenkovision_test",
    database="davidenkovision_dev",
    user="postgres",
    # password="4136121025")
    password="postgres")

cur = conn.cursor()

# statement = 'INSERT INTO entries_contests(contest_id, entry_id) VALUES (%s, %s);'

final_entry_list = [1, 2, 4, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 25, 27, 29, 31, 34, 35, 36, 38, 40]
sf1_list = [3, 32, 20, 39, 27, 6, 4, 34, 36, 30, 29, 17, 25, 37, 26, 18, 22]
sf2_list = [13, 24, 23, 9, 35, 38, 33, 15, 28, 19, 21, 12, 2, 5, 11, 14, 31]

# for entry_id in sf2_list:
#     cur.execute(statement, (4, entry_id))
#
# conn.commit()


# INJECTING TOKENS INFO

def token_injection_calculation(liked, qualify):
    # return int(math.e**((liked + qualify)/100))
    return int(math.e**((liked)/100))


# for semifinalists -- likes in poll, qualify
# for autofinalists -- likes in poll, likes in poll / 2
coefficients = {
    1: token_injection_calculation(244,244/2),
    2: token_injection_calculation(229,102),
    3: token_injection_calculation(150,70),
    4: token_injection_calculation(281,114),
    5: token_injection_calculation(163,49),
    6: token_injection_calculation(133,41),
    7: token_injection_calculation(154,154/2),
    8: token_injection_calculation(154,154/2),
    9: token_injection_calculation(106,32),
    10: token_injection_calculation(82,82/2),
    11: token_injection_calculation(235,92),
    12: token_injection_calculation(168,96),
    13: token_injection_calculation(228,127),
    14: token_injection_calculation(110,59),
    15: token_injection_calculation(459,139),
    16: token_injection_calculation(201,201/2),
    17: token_injection_calculation(147,84),
    18: token_injection_calculation(297,156),
    19: token_injection_calculation(142,48),
    20: token_injection_calculation(179,128),
    21: token_injection_calculation(246,103),
    22: token_injection_calculation(119,94),
    23: token_injection_calculation(171,88),
    24: token_injection_calculation(46,29),
    25: token_injection_calculation(112,74),
    26: token_injection_calculation(81,17),
    27: token_injection_calculation(182,124),
    28: token_injection_calculation(97,36),
    29: token_injection_calculation(113,78),
    30: token_injection_calculation(188,60),
    31: token_injection_calculation(286,95),
    32: token_injection_calculation(81,21),
    33: token_injection_calculation(108,54),
    34: token_injection_calculation(118,90),
    35: token_injection_calculation(186,96),
    36: token_injection_calculation(319,160),
    37: token_injection_calculation(99,46),
    38: token_injection_calculation(349,81),
    39: token_injection_calculation(127,33),
    40: token_injection_calculation(245,245/2),
}

all_sum = 0

# for k, v in coefficients.items():
#     all_sum += v

for k in sf1_list:
    all_sum += coefficients[k]

print(coefficients, all_sum)

statement = 'INSERT INTO entries_status(entry_id, betting_category_id, total_sum, coefficient) VALUES (%s, %s, %s, %s);'

for k in sf1_list:
# for k, v in coefficients.items():
    cur.execute(statement, (k, 4, coefficients[k], coefficients[k]/all_sum))

conn.commit()

