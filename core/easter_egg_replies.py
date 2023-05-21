from core.db_connection import cur


def get_easter_egg_replies() -> tuple:
    """Method that fetches a list of all ongoing contests."""

    query = "SELECT reply FROM easter_egg_replies;"

    cur.execute(query)
    replies = cur.fetchall()
    replies_list = []

    for reply in replies:
        replies_list.append(reply[0])

    return tuple(replies_list)
