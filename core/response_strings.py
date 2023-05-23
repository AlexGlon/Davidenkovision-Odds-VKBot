import random

from core.easter_egg_replies import get_easter_egg_replies
from core.enums import EasterEggReplyEnum

# TODO: implement localization


ADMIN_CATEGORY_CLOSED = "Данная категория ставок была успешно закрыта."
ADMIN_CATEGORY_OPENED = "Данная категория ставок была успешно открыта."
ADMIN_INVALID_CATEGORY_TO_CLOSE = (
    "Hеверный номер категории! "
    'Повторите процесс заново, отправив сообщение с текстом "закрыть категорию".'
)
ADMIN_INVALID_CATEGORY_TO_OPEN = (
    "Hеверный номер категории! "
    'Повторите процесс заново, отправив сообщение с текстом "открыть категорию".'
)
ADMIN_NO_CATEGORIES_TO_CLOSE = "Все категории ставок на данный момент закрыты."
ADMIN_NO_CATEGORIES_TO_OPEN = "Все категории ставок на данный момент открыты."
ADMIN_SELECT_CATEGORY_TO_CLOSE = "Выберите категорию ставок для закрытия:\n\n"
ADMIN_SELECT_CATEGORY_TO_OPEN = "Выберите категорию ставок для открытия:\n\n"
BET_CANCELLATION = "Отмена ставки"
BET_CANCELLATION_ABORTED = "Ставка не была отменена."
BET_CANCELLATION_SUCCESS = (
    "Ставка отменена. Поставленные на неё фишки вернулись на ваш баланс."
)
BET_COEFFICIENT_HAS_BEEN_MODIFIED = (
    "Коэффициент данной ставки был изменён на актуальный, "
    "так как вы провели в данном меню более 5 минут."
)
BET_CREATION_DATE = "Дата ставки"
BET_PLACED_SUCCESSFULLY = (
    "Ставка сделана! "
    "Вы можете увидеть её в списке своих ставок, "
    'введя сообщение с текстом "мои ставки" или "история ставок". {phrase}\n\n'
)
BETTING_CATEGORY_CLOSED_FOR_CANCELLING_BETS = (
    "Данная категория ставок больше не принимает ставки, "
    "поэтому отменить данную ставку нельзя."
)
BETTING_CATEGORY_CLOSED_FOR_PLACING_BETS = (
    "Данная категория ставок больше не принимает ставки."
)
COEFFICIENT = "Коэффициент"
CONFIRM_BET_CANCELLATION = (
    "Вы уверены, что хотите отменить данную ставку? "
    "Если уверены, то ответьте на это сообщение порядковым номером ставки.\n\n"
)
HIDDEN_COEFFICIENT = "Временно скрыт"
INVALID_BET_TO_CANCEL_NUMBER = (
    "Hеверный номер ставки! "
    'Повторите процесс заново, отправив сообщение с текстом "отменить ставку".'
)
INVALID_CATEGORY_TO_PLACE_BETS_ON = (
    "Hеверный номер категории! "
    'Повторите процесс заново, отправив сообщение с текстом "ставка".'
)
INVALID_CATEGORY_TO_SHOW_BET_STATUSES = (
    "Hеверный номер категории! "
    'Повторите процесс заново, отправив сообщение с текстом "ставки".'
)
INVALID_CONTEST_TO_SHOW_ENTRIES = (
    "Hеверный номер конкурса! "
    'Повторите процесс заново, отправив сообщение с текстом "заявки".'
)
INVALID_INPUT_WHILE_PLACING_A_BET = (
    "Неверно введены номер заявки и/или количество фишек для ставки! "
    'Повторите процесс заново, отправив сообщение с текстом "ставка".'
)
NO_BETS_TO_CANCEL = "У вас нет ставок, которые можно отменить."
NO_BETS_TO_SHOW = "Вы ещё не делали никаких ставок."
NO_BETS_TO_SHOW_FOR_CURRENT_CONTESTS = (
    "Вы ещё не делали никаких ставок на текущие конкурсы."
)
NO_CATEGORIES_TO_PLACE_BETS_ON = "На данный момент нет открытых категорий ставок."
NO_CATEGORIES_TO_SHOW_BET_STATUSES = "На данный момент нет текущих категорий ставок."
NO_CONTESTS_TO_SHOW_ENTRIES = "На данный момент нет текущих конкурсов."
NO_PERMISSION_FOR_ADMIN_COMMAND = (
    "Вы не можете воспользоваться этой командой, "
    "так как она доступна только для администраторов."
)
NO_POINTS_TO_SPEND = "Вы не можете сделать ставку, так как у вас на балансе 0 фишек."
NO_VISIBLE_CATEGORIES_TO_SHOW_BET_STATUSES = (
    "На данный момент нет текущих и нескрытых категорий ставок."
)
POINTS = "Фишек поставлено"
POINTS_RETURNED = "Фишек возвращено"
SELECT_BET_TO_CANCEL = "Выберите ставку, которую вы хотите отменить:\n\n"
SELECT_CATEGORY_TO_PLACE_BETS_ON = "Выберите категорию ставок:\n\n"
SELECT_CATEGORY_TO_SHOW_BET_STATUSES = (
    "Выберите категорию ставок для просмотра коэффициентов:\n\n"
)
SELECT_CONTEST_TO_SHOW_ENTRIES = (
    "Выберите конкурс, заявки из которого вы хотите увидеть:\n\n"
)
# TODO: check this newline thing if it works as expected
SELECT_ENTRY_TO_PLACE_BETS_ON = (
    "Введите номер заявки, на которую хотите сделать ставку, "
    'и количество фишек через пробел или новой строкой. К примеру, "1 69" или\n\n1\n69\n\n'
)


BET_PLACEMENT_EASTER_EGG_REPLIES = get_easter_egg_replies(EasterEggReplyEnum.BET_PLACED)
EASTER_EGG_REPLIES = get_easter_egg_replies(EasterEggReplyEnum.REGULAR)
WELCOME_EASTER_EGG_REPLIES = get_easter_egg_replies(EasterEggReplyEnum.WELCOME)


def get_bet_placement_easter_egg_reply() -> str:
    return random.choice(BET_PLACEMENT_EASTER_EGG_REPLIES)


def get_regular_easter_egg_reply() -> str:
    return random.choice(EASTER_EGG_REPLIES)


def get_welcome_easter_egg_reply() -> str:
    return random.choice(WELCOME_EASTER_EGG_REPLIES)
