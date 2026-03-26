import time
import logging
import functools
from typing import Callable


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


def retry(retries=3, delay=2.0, exceptions=(Exception)):

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    logger.warning(
                        f"[retry] {func.__name__} attempt {attempt}/{retries} failed: {exc}"
                    )
                    if attempt < retries:
                        time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def rate_limited(max_per_minute=10):
    min_interval = 60.0 / max_per_minute
    last_called = {"time": 0.0}

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """ 
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    def decorator(func):

        # --------------------------------
        # :: Logger Variable
        # --------------------------------

        """
        Logger for the bot module. This logger will be used to log important events, warnings,
        and errors related to the bot's operation.
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called["time"]
            wait = min_interval - elapsed
            if wait > 0:
                time.sleep(wait)
            result = func(*args, **kwargs)
            last_called["time"] = time.time()
            return result

        return wrapper

    return decorator


# --------------------------------
# :: Logger Variable
# --------------------------------

""" 
Logger for the bot module. This logger will be used to log important events, warnings,
and errors related to the bot's operation.
"""


def log_action(func):

    # --------------------------------
    # :: Logger Variable
    # --------------------------------

    """
    Logger for the bot module. This logger will be used to log important events, warnings,
    and errors related to the bot's operation.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"[action] Starting {func.__name__}")
        start = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"[action] Finished {func.__name__} in {elapsed:.2f}s")
            return result
        except Exception as exc:
            elapsed = time.time() - start
            logger.error(f"[action] {func.__name__} failed after {elapsed:.2f}s: {exc}")
            raise

    return wrapper
