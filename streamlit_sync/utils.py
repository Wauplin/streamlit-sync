"""Streamlit-sync specific utils."""
from . import st_hack


def is_synced(widget_id: str) -> bool:
    """Check is widget is a synced one or not."""
    return (
        NOT_SYNCED_PREFIX not in widget_id
        and st_hack.STREAMLIT_INTERNAL_KEY_PREFIX not in widget_id
    )


def get_not_synced_key(user_key: str) -> str:
    """Return a widget key that is explicitely not synced."""
    return NOT_SYNCED_PREFIX + "_" + user_key


NOT_SYNCED_PREFIX = "$NOT_SYNCED$"

# Private keys used by streamlit-sync
LAST_SYNCED_KEY = get_not_synced_key("$LAST_SYNCED$")
ROOM_NAME_KEY = get_not_synced_key("$ROOM_NAME$")
