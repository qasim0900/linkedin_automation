from utils.logger import setup_logger
from utils.human_behavior import HumanBehavior
from utils.decorators import rate_limited, log_action
from utils.helpers import retry, safe_get, format_profile_url

# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def get_human_behavior(driver):
    return HumanBehavior(driver)


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

__all__ = [
    "HumanBehavior",
    "get_human_behavior",
    "retry",
    "safe_get",
    "format_profile_url",
    "setup_logger",
    "rate_limited",
    "log_action",
]
