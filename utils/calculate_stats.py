import json
from fractions import Fraction


def coefficient_calculation(coef):
    """Calculates bet coefficients of each entry."""
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
        return int(round(preliminary / 5, 0) * 5)
    elif preliminary < 1000:
        return int(round(preliminary / 50, 0) * 50)
    elif preliminary >= 1000:
        return 1000


# =====================================================================================================
#                                              OLD CODE
# =====================================================================================================


def calculate(entry_id, tokens):
    """Updates stats of each entry after any operation with a bet."""
    with open("stats.json", "r") as file:
        stats = json.load(file)
    stats["total"] += tokens
    stats["entry_stats"][entry_id]["tokens_sum"] += tokens
    # TODO: change this range limit while enginizing the bot
    for i in range(1, 27):
        stats["entry_stats"][i]["coef"] = (
            stats["entry_stats"][i]["tokens_sum"] / stats["total"]
        )
        stats["entry_stats"][i]["current_coef"] = coefficient_calculation(
            stats["entry_stats"][i]["coef"]
        )
    with open("stats.json", "w") as file:
        json.dump(stats, file, indent=4)
