from core.db_connection import cur
from core.menu_step_decorator import menu_decorator
from core.response_strings import CURRENT_BALANCE, NO_BALANCE_TO_SHOW


# TODO: rework this!!
@menu_decorator()
def show_current_balance(**kwargs):
    """Method that fetches a list of all ongoing betting categories for further closing."""

    user_id = kwargs.get("user_id")

    query = (
        "SELECT total FROM balances "
        "LEFT JOIN balances_contests bc on balances.balance_id = bc.balance_id "
        "LEFT JOIN contests c on c.contest_id = bc.contest_id "
        "WHERE c.ongoing = TRUE "
        f"AND user_id = {user_id}"
    )

    cur.execute(query)
    balances = cur.fetchall()

    if len(balances) == 0:
        return NO_BALANCE_TO_SHOW, {"terminate_menu": True}

    current_balance_value = balances[0][0]

    response = CURRENT_BALANCE.format(value=current_balance_value)

    return response, {"terminate_menu": True}
