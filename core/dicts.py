# a dictionary that contains information about user's last visited menu
# and temporary information from previous menus

USER_STATES = {}

# a dictionary that contains all menu step handler functions
# and menu step handlers that follow

NEXT_DIALOGUE_STEP_HANDLERS = {}

# a dictionary that contains all regex patterns
# that are valid for invoking a particular menu step
# TODO: a decorator that uses this dictionary for each menu step

DIALOGUE_STEP_INVOKING_MESSAGES = {}
