import re
from datetime import datetime, timezone

VALID_ID = re.compile(r"^\d{15,25}$")


def utc_now():
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def clean_text(value, max_length=4000):
    """Trim whitespace and limit length."""
    if value is None:
        return ""
    return str(value).strip()[:max_length]


def valid_discord_id(value):
    """Validate Discord snowflake."""
    if value is None:
        return False
    return bool(VALID_ID.fullmatch(str(value)))


def is_enabled(value):
    """Convert HTML checkbox to boolean."""
    return str(value).lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def bool_to_int(value):
    return 1 if value else 0


def int_to_bool(value):
    return bool(int(value))


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def truncate(text, length=100):
    text = str(text)

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


def format_status(status):

    colours = {
        "Pending": "#facc15",
        "Approved": "#22c55e",
        "Accepted": "#22c55e",
        "Implemented": "#3b82f6",
        "Rejected": "#ef4444",
        "Open": "#22c55e",
        "Closed": "#ef4444",
        "Running": "#3b82f6",
        "Completed": "#22c55e",
        "Failed": "#ef4444",
    }

    return colours.get(status, "#6b7280")


def make_application_text(
    name,
    age,
    timezone_name,
    experience,
    reason,
):

    return (
        f"Name: {name}\n"
        f"Age: {age}\n"
        f"Timezone: {timezone_name}\n"
        f"Experience: {experience}\n\n"
        f"Reason:\n{reason}"
    )


def normalise_action(action):

    if not action:
        return ""

    return str(action).strip().lower()


VALID_AUTOMOD_RULES = {
    "bad_words",
    "spam",
    "invite_links",
    "caps_spam",
    "mass_mentions",
}


VALID_MOD_ACTIONS = {
    "warn",
    "kick",
    "ban",
    "unban",
    "timeout",
    "untimeout",
    "purge",
}


SUGGESTION_STATUS = {
    "Pending",
    "Approved",
    "Rejected",
    "Implemented",
}


APPEAL_STATUS = {
    "Pending",
    "Accepted",
    "Rejected",
}


APPLICATION_STATUS = {
    "Pending",
    "Accepted",
    "Rejected",
}
