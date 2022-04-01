from streamlit_sync.utils import (
    LAST_SYNCED_KEY,
    ROOM_NAME_KEY,
    get_not_synced_key,
    is_synced,
)


def test_is_synced() -> None:
    """Test `is_synced`."""
    assert is_synced("custom_user_key")
    assert not is_synced("$NOT_SYNCED$_custom_user_key")

    # Keys used internally by streamlit-sync
    assert not is_synced(LAST_SYNCED_KEY)
    assert not is_synced(ROOM_NAME_KEY)


def test_get_not_synced_key() -> None:
    """Test `get_not_synced_key`."""
    assert get_not_synced_key("custom_user_key") == "$NOT_SYNCED$_custom_user_key"
