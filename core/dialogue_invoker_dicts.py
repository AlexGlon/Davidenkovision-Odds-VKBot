# a dictionary that contains all regex patterns
# that are valid for invoking a particular menu step

DIALOGUE_STEP_INVOKING_PATTERNS = {
    'cancel_selected_bet': r'^\d+$',
    'get_bet_statuses_to_show': r'^\d+$',
    'get_bet_cancellation_confirmation': r'^\d+$',
    'get_bet_category_to_bet_on': r'^ставка$',
    'get_bets_eligible_for_deletion': r'^отменить ставку$',
    'get_category_to_show_bet_statuses': r'^ставки$',
    'get_contest_to_show_entries': r'^заявки$',
    'get_current_contests_bets_history': r'^мои ставки$',
    'get_entries_to_show': r'^\d+$',
    'get_entry_to_bet_on': r'^\d+$',
    'get_user_bets_history': r'^история ставок$',
    'validate_and_accept_incoming_bet': r'^\d+\s\d+$',
}
