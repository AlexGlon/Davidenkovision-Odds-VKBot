from core.db_connection import cur
from core.dotenv_variables import COEFFICIENT_OBSCURITY
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    INVALID_CATEGORY_TO_SHOW_BET_STATUSES,
    NO_CATEGORIES_TO_SHOW_BET_STATUSES,
    NO_VISIBLE_CATEGORIES_TO_SHOW_BET_STATUSES,
    SELECT_CATEGORY_TO_SHOW_BET_STATUSES,
)
from flags import country_dict
from utils.calculate_stats import coefficient_calculation


@menu_decorator()
def get_category_to_show_bet_statuses(**kwargs):
    """Method that fetches a list of all ongoing betting categories."""

    statement = 'SELECT row_number() OVER (ORDER BY betting_categories.betting_category_id), betting_category_id, ' \
                'c.name, ct.name, bct.name ' \
                'FROM betting_categories ' \
                'FULL JOIN betting_category_types bct on bct.type_id = betting_categories.category_type ' \
                'LEFT JOIN contests c on c.contest_id = betting_categories.contest_id ' \
                'LEFT JOIN contests_types ct on ct.type_id = c.type ' \
                'WHERE ongoing = TRUE ' \
                f'{"AND c.deadline_date < now()" if COEFFICIENT_OBSCURITY else ""};'

    cur.execute(statement)
    categories = cur.fetchall()

    if len(categories) == 0:
        if COEFFICIENT_OBSCURITY:
            return NO_VISIBLE_CATEGORIES_TO_SHOW_BET_STATUSES, {'terminate_menu': True}
        else:
            return NO_CATEGORIES_TO_SHOW_BET_STATUSES, {'terminate_menu': True}

    if len(categories) == 1:
        response, extra_info = get_bet_statuses_to_show(invoking_message=str(categories[0][1]))

        return response, {'terminate_menu': True}

    response = SELECT_CATEGORY_TO_SHOW_BET_STATUSES

    for category in categories:
        response += f"{category[0]}. {category[2]} {category[3] if category[3] else ''} {category[4]}\n"

    return response, {}


@menu_decorator()
def get_bet_statuses_to_show(**kwargs):
    """Method that fetches a list of all entries and their coefficients
    from a specified betting category."""

    category_id = kwargs.get('invoking_message')

    statement = 'SELECT row_number() OVER (ORDER BY coefficient DESC), ' \
                'c.name, e.year_prefix, e.artist, e.title, ' \
                'coefficient ' \
                'FROM entries_status ' \
                'LEFT JOIN entries e on e.entry_id = entries_status.entry_id ' \
                'LEFT JOIN countries c on e.country_id = c.country_id ' \
                f'WHERE betting_category_id = {category_id} ' \
                'ORDER BY coefficient DESC;'

    cur.execute(statement)
    entries = cur.fetchall()

    if len(entries) == 0:
        return INVALID_CATEGORY_TO_SHOW_BET_STATUSES, {}

    response = ''

    for entry in entries:
        response += f"{entry[0]}. " \
                    f"{country_dict.get(entry[1])} {entry[1]} {' ' + entry[2] + ' |' if entry[2] else ' |'} " \
                    f"{entry[3]} -- {entry[4]} | {coefficient_calculation(entry[5])}\n"

    return response, {}
