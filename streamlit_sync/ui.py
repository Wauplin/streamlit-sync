"""Define a sidebar UI to enter and exit rooms.

The select_room widget is just a simple example of how to use the ./rooms.py API.
"""

from pathlib import Path
from typing import Optional, Set, Union

import streamlit as st

from .rooms import enter_room, exit_room
from .synced_state import get_existing_room_names, get_synced_state
from .utils import ROOM_NAME_KEY, get_not_synced_key


def select_room_widget(cache_dir: Optional[Union[str, Path]]) -> str:
    if st.session_state.get(ROOM_NAME_KEY) is not None:
        # Is already in a room
        room_name = st.session_state[ROOM_NAME_KEY]
        with st.sidebar.expander(
            f'Synced room "{room_name}" ({_get_room_status(room_name)})'
        ):
            if st.button("Exit room"):
                exit_room()
        return room_name

    else:
        st.sidebar.title("Select a synced room")

        room_name = None
        existing_rooms = get_existing_room_names() | _list_from_cache_dir(cache_dir)
        options = [None]  # None for "create new room"
        if existing_rooms:
            options += sorted(existing_rooms)

            room_name = st.sidebar.radio(
                "Existing rooms",
                options,
                key=get_not_synced_key("existing_rooms"),
                format_func=_radio_format_func,
            )

        # Enter room if not None
        if room_name is not None:
            enter_room(room_name)

        # Else: create new room
        with st.sidebar.form(
            key=get_not_synced_key("select_room_form"), clear_on_submit=True
        ):
            new_room_name = st.text_input("New room name")
            submit = st.form_submit_button(label="Create")

        if submit:
            enter_room(new_room_name)

        st.stop()

    raise NotImplementedError


def _radio_format_func(room_name: Optional[str]) -> Optional[str]:
    if room_name is None:
        return "Create new room"
    return f"{room_name} ({_get_room_status(room_name)})"


def _get_room_status(room_name: str) -> str:
    nb_sessions = get_synced_state(room_name).nb_active_sessions
    if nb_sessions == 0:
        return "empty"
    elif nb_sessions == 1:
        return "1 active session"
    else:
        return f"{nb_sessions} active sessions"


def _list_from_cache_dir(cache_dir: Optional[Union[str, Path]]) -> Set[str]:
    """List existing rooms saved in cache dir."""
    if cache_dir is None:
        return set()

    cache_dir = Path(cache_dir)
    if not cache_dir.exists():
        return set()

    return {path.name for path in cache_dir.iterdir() if path.is_dir()}
