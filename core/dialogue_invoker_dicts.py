# a dictionary that contains all regex patterns
# that are valid for invoking a particular menu step

DIALOGUE_STEP_INVOKING_PATTERNS = {
    'get_bet_statuses_to_show': r'^\d+',
    'get_category_to_show_bet_statuses': r'^ставки$',
    'get_contest_to_show_entries': r'^заявки$',
    'get_current_contests_bets_history': r'^мои ставки$',
    'get_entries_to_show': r'^\d+',
    'get_user_bets_history': r'^история ставок$',
}
