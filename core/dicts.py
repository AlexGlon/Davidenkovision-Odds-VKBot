from show_bets import get_current_contests_bets_history
from show_entries import get_contest_to_show_entries, get_entries_to_show

FIRST_DIALOGUE_STEPS = {
    r'^заявки$': get_contest_to_show_entries,
    r'^мои ставки$': get_current_contests_bets_history,
}

# a dictionary that contains all menu step handler functions
# and menu step handlers that follow

NEXT_DIALOGUE_STEP_HANDLERS = {
    get_contest_to_show_entries: get_entries_to_show,
    get_current_contests_bets_history: None,
    get_entries_to_show: None,
}
