from admin_tools.admin_command_access_decorator import admin_command_decorator
from core.db_connection import conn, cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import (
    ADMIN_CATEGORY_CLOSED,
    ADMIN_INVALID_CATEGORY_TO_CLOSE,
    ADMIN_NO_CATEGORIES_TO_CLOSE,
    ADMIN_SELECT_CATEGORY_TO_CLOSE,
)


@admin_command_decorator()
@menu_decorator()
def admin_get_category_to_close(**kwargs):
    """Method that fetches a list of all ongoing betting categories for further closing."""

    query = (
        "SELECT betting_category_id, c.name, ct.name, bct.name "
        "FROM betting_categories "
        "FULL JOIN betting_category_types bct on bct.type_id = betting_categories.category_type "
        "LEFT JOIN contests c on c.contest_id = betting_categories.contest_id "
        "LEFT JOIN contests_types ct on ct.type_id = c.type "
        "WHERE accepts_bets = TRUE;"
    )

    cur.execute(query)
    categories = cur.fetchall()

    if len(categories) == 0:
        return ADMIN_NO_CATEGORIES_TO_CLOSE, {"terminate_menu": True}

    response = ADMIN_SELECT_CATEGORY_TO_CLOSE

    for category in categories:
        response += f"{category[0]}. {category[1]} {category[2] if category[2] else ''} {category[3]}\n"

    return response, {}


@admin_command_decorator()
@menu_decorator()
def admin_close_category(**kwargs):
    """Method that fetches a list of all entries and their coefficients
    from a specified betting category."""

    category_id = kwargs.get("invoking_message")

    query = (
        f"UPDATE betting_categories "
        f"SET accepts_bets = FALSE "
        f"WHERE betting_category_id = {category_id};"
    )

    cur.execute(query)
    conn.commit()

    # TODO: if we send a number of a category that's already closed, we skip this block...
    if cur.rowcount == 0:
        return ADMIN_INVALID_CATEGORY_TO_CLOSE, {}

    response = ADMIN_CATEGORY_CLOSED

    return response, {}