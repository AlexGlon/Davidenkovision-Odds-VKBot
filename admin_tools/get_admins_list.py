from core.db_connection import cur


def get_admins_list() -> tuple:
    """Method that fetches a list of all current admins on bot setup."""

    query = "SELECT user_id FROM admins;"

    cur.execute(query)
    admins = cur.fetchall()
    admins_list = []

    for admin in admins:
        admins_list += admin

    return tuple(admins_list)
