from show_entries import get_contest_to_show_entries, get_entries_to_show

FIRST_DIALOGUE_STEPS = {
    r'^заявки$': get_contest_to_show_entries,
}

# a dictionary that contains all menu step handler functions
# and menu step handlers that follow

NEXT_DIALOGUE_STEP_HANDLERS = {
    get_contest_to_show_entries: get_entries_to_show,
    get_entries_to_show: None,
}
