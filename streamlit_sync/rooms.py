"""High level API to manage rooms."""

import streamlit as st

from . import st_hack
from .exceptions import StreamlitSyncException
from .synced_state import get_synced_state
from .utils import LAST_SYNCED_KEY, ROOM_NAME_KEY


def enter_room(room_name: str) -> None:
    """Enter a room from current session (register and rerun)."""
    st.session_state[ROOM_NAME_KEY] = room_name
    st.experimental_rerun()


def exit_room() -> None:
    """Exit room from current session (unregister, reset values and rerun)."""
    # Forget the room
    try:
        room_name = st.session_state.pop(ROOM_NAME_KEY)
    except KeyError:
        raise StreamlitSyncException("Cannot exit a room: currently not in a room.")

    del st.session_state[LAST_SYNCED_KEY]

    # Unregister from room
    synced_state = get_synced_state(room_name)
    synced_state.unregister_session()

    # Reset values set by room
    st_hack.del_internal_values(synced_state.state.keys())

    # Rerun to re-update frontend accordingly
    st.experimental_rerun()


def delete_room(room_name: str) -> None:
    """Delete a room."""
    get_synced_state(room_name).delete()
