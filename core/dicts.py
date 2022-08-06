from show_entries import get_contest_to_show_entries, get_entries_to_show

# a dictionary that contains information about user's last visited menu
# and temporary information from previous menus

USER_STATES = {

}

# a dictionary that contains all menu step handler functions
# and menu step handlers that follow

NEXT_DIALOGUE_STEP_HANDLERS = {
    get_contest_to_show_entries: get_entries_to_show,
}
