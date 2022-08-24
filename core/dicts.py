from bets.accept_bet import (
    get_bet_category_to_bet_on,
    get_entry_to_bet_on,
    validate_and_accept_incoming_bet,
)
from bets.cancel_bet import (
    cancel_selected_bet,
    get_bet_cancellation_confirmation,
    get_bets_eligible_for_deletion,
)
from bets.show_bets import get_current_contests_bets_history, get_user_bets_history
from bets.show_current_statuses import (
    get_bet_statuses_to_show,
    get_category_to_show_bet_statuses,
)
from show_entries import get_contest_to_show_entries, get_entries_to_show

FIRST_DIALOGUE_STEPS = {
    r"^заявки$": get_contest_to_show_entries,
    r"^история ставок$": get_user_bets_history,
    r"^мои ставки$": get_current_contests_bets_history,
    r"^отменить ставку$": get_bets_eligible_for_deletion,
    r"^ставка$": get_bet_category_to_bet_on,
    r"^ставки$": get_category_to_show_bet_statuses,
}

# a dictionary that contains all menu step handler functions
# and menu step handlers that follow

NEXT_DIALOGUE_STEP_HANDLERS = {
    cancel_selected_bet: None,
    get_bet_statuses_to_show: None,
    get_bet_cancellation_confirmation: cancel_selected_bet,
    get_bet_category_to_bet_on: get_entry_to_bet_on,
    get_bets_eligible_for_deletion: get_bet_cancellation_confirmation,
    get_category_to_show_bet_statuses: get_bet_statuses_to_show,
    get_contest_to_show_entries: get_entries_to_show,
    get_current_contests_bets_history: None,
    get_entries_to_show: None,
    get_entry_to_bet_on: validate_and_accept_incoming_bet,
    get_user_bets_history: None,
    validate_and_accept_incoming_bet: None,
}

SKIPPING_NEXT_DIALOGUE_STEP_HANDLERS = {
    get_bet_category_to_bet_on: validate_and_accept_incoming_bet,
    # TODO: test this
    get_bets_eligible_for_deletion: cancel_selected_bet,
}
