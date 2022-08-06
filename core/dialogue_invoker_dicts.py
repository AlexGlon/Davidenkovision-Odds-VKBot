# a dictionary that contains all regex patterns
# that are valid for invoking a particular menu step
# TODO: a decorator that uses this dictionary for each menu step

DIALOGUE_STEP_INVOKING_PATTERNS = {
    'get_contest_to_show_entries': r'^заявки$',
    'get_entries_to_show': r'^\d+',
}
