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
# :: Ensure Logged In Function
# --------------------------------

""" 
Function to ensure that the bot is logged in. It checks if there is an existing session and if it is still valid. 
If the session is valid, it will continue using it. If the session has expired or if a new session is forced, 
it will attempt to log in again. The function returns True if the login is successful,
"""


def ensure_logged_in(auth_instance, force_new_session = False):
    if not force_new_session and auth_instance.is_logged_in:
        if auth_instance.verify_session():
            logger.debug("Existing session is still valid")
            return True
        logger.info("Session expired — attempting refresh")

    return auth_instance.login(force_new_session=force_new_session)


# --------------------------------
# :: Safe Logout Function
# --------------------------------

""" 
Function to safely log out of the bot. It attempts to log out and catches any exceptions that may occur during the process. 
If an exception occurs, it logs a warning and returns False, indicating that the logout was not successful
"""


def safe_logout(auth_instance):
    try:
        return auth_instance.logout()
    except Exception as exc:
        logger.warning(f"Logout error (ignored): {exc}")
        return False
