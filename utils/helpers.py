import re
import time
import logging


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

logger = logging.getLogger(__name__)



# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

def retry(func, retries = 3, delay = 2.0, exceptions=(Exception,)):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return func()
        except exceptions as exc:
            last_exc = exc
            logger.warning(f"Attempt {attempt}/{retries} failed: {exc}")
            if attempt < retries:
                time.sleep(delay)
    raise last_exc



# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

def safe_get(d, *keys, default=None):
    current = d
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
    return current



# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

def format_profile_url(url):
    if not url:
        return None
    url = re.sub(r"\?.*$", "", url).rstrip("/")
    if "linkedin.com/in/" not in url:
        return None
    return url


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""

def chunk(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]
