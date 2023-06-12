from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch

from streamlit_sync import st_hack
from streamlit_sync.exceptions import StreamlitSyncException
from streamlit_sync.st_hack import (
    is_form_submitter_value,
    is_trigger_value,
    widget_id_to_user_key,
)


def test_is_form_submitter_value() -> None:
    """Test `is_form_submitter_value`."""
    assert is_form_submitter_value("FormSubmitter:my_form-Submit")
    assert is_form_submitter_value("FormSubmitter:customkey-Submit")
    assert not is_form_submitter_value("customkey")


def test_is_trigger_value() -> None:
    """Test `is_trigger_value`."""
    mock = MagicMock()
    mock._new_widget_state.widget_metadata.__contains__.side_effect = (
        lambda key: key == "customkey"
    )

    # Widget was not updated
    assert not is_trigger_value("key", mock)

    # Widget was updated but not a trigger_value
    assert not is_trigger_value("customkey", mock)

    # Widget was updated and it's a trigger_value
    mock._new_widget_state.widget_metadata.__getitem__().value_type = "trigger_value"
    assert is_trigger_value("customkey", mock)


def test_widget_id_to_user_key(monkeypatch: MonkeyPatch) -> None:
    """Test `widget_id_to_user_key`."""
    monkeypatch.setattr(st_hack, "is_keyed_widget_id", lambda x: x != "not_keyed")

    assert widget_id_to_user_key("not_keyed") == "not_keyed"
    assert (
        widget_id_to_user_key(
            "$$GENERATED_WIDGET_KEY-a57f8cd0ef6469c61f435e5eb8097cf7-customkey"
        )
        == "customkey"
    )

    with pytest.raises(StreamlitSyncException):
        widget_id_to_user_key("auto_generated_widget_id_with_wrong_format")
