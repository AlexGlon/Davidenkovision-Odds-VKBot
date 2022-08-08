from bets.show_current_statuses import get_bet_statuses_to_show, get_category_to_show_bet_statuses
from show_bets import get_current_contests_bets_history, get_user_bets_history
from show_entries import get_contest_to_show_entries, get_entries_to_show

FIRST_DIALOGUE_STEPS = {
    r'^заявки$': get_contest_to_show_entries,
    r'^история ставок$': get_user_bets_history,
    r'^мои ставки$': get_current_contests_bets_history,
    r'^ставки$': get_category_to_show_bet_statuses,
}

# a dictionary that contains all menu step handler functions
# and menu step handlers that follow

NEXT_DIALOGUE_STEP_HANDLERS = {
    get_bet_statuses_to_show: None,
    get_category_to_show_bet_statuses: get_bet_statuses_to_show,
    get_contest_to_show_entries: get_entries_to_show,
    get_current_contests_bets_history: None,
    get_entries_to_show: None,
    get_user_bets_history: None,
}
