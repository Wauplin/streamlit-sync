from pathlib import Path
from typing import Optional, Union

from .rooms import delete_room, enter_room, exit_room
from .synced_state import get_synced_state as _get_synced_state
from .ui import select_room_widget
from .utils import get_not_synced_key


class sync:
    """Sync your Streamlit app with other sessions of the room !"""

    def __init__(
        self, room_name: str, cache_dir: Optional[Union[str, Path]] = None
    ) -> None:
        if cache_dir is not None:
            # Attach to disk from caching
            _get_synced_state(room_name).attach_to_disk(Path(cache_dir))

        self.room_name = room_name
        self._inner_sync()

    def __enter__(self) -> "sync":
        return self

    def __exit__(self, type, value, traceback) -> None:  # type: ignore
        self._inner_sync()

    def _inner_sync(self) -> None:
        synced_state = _get_synced_state(self.room_name)
        synced_state.register_session()
        synced_state.sync()
