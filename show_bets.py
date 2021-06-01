import json
import flags
import accept_bet


# TODO: user can check his bets and delete any if he wishes
def entry_point(user_id):
    user_data = accept_bet.load_data(user_id)
    if not user_data['bets']:
        return "У вас на данный момент нет никаких ставок."

    with open('entries.json', 'r') as file:
        entries = json.load(file)
    response = 'Ваши ставки:\n'
    for bet in user_data['bets']:
        entry = entries[bet['entry_id']-1]
        line = f"{user_data['bets'].index(bet)+1}. {flags.country_dict[entry['country']]} {entry['country']}"
        line_year = (lambda x: ' ' if x == None else f" {x} ")(entry['year'])
        line_entry = f" | {entry['artist']} — {entry['entry']} | {bet['tokens']} (Коэффициент: {bet['coefficient']})\n"
        response += line + line_year + line_entry

    return response
