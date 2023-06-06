"""Module that contains all calls to internal APIs of Streamlit.

It is most likely that this module will break in future updates of Streamlit.
"""
import re
from typing import Any, Iterable, Mapping, Optional, Tuple

from streamlit.web.server import Server
from streamlit.runtime.state.session_state import (
    STREAMLIT_INTERNAL_KEY_PREFIX,
    SessionState,
)

from streamlit.runtime.state.common import GENERATED_WIDGET_ID_PREFIX

from .exceptions import StreamlitSyncException

try:
    from streamlit.runtime.state import get_session_state
except ImportError:
    # streamlit < 1.7
    from streamlit.state.session_state import get_session_state

try:
    from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx
except ImportError:
    try:
        # streamlit < 1.7
        from streamlit.script_run_context import get_script_run_ctx
    except ImportError:
        # streamlit < 1.4
        from streamlit.report_thread import get_report_ctx as get_script_run_ctx

from streamlit.runtime import get_instance as get_runtime_instance

try:
    from streamlit.runtime.state.session_state import is_keyed_widget_id
except ImportError:
    from streamlit.state.session_state import is_keyed_widget_id as is_keyed_widget_id


_WIDGET_ID_REGEX = re.compile(
    re.escape(GENERATED_WIDGET_ID_PREFIX) + r"-[0-9a-f]{32}-(?P<user_key>.*)"
)


def widget_id_to_user_key(widget_id: str) -> str:
    """Return user key if widget is a keyed-widget, else the widget id itself."""
    if is_keyed_widget_id(widget_id):
        match = _WIDGET_ID_REGEX.match(widget_id)
        if match is None:
            # If broken, look at implementation in
            #   - https://github.com/streamlit/streamlit/blob/develop/lib/streamlit/state/widgets.py#L258 # noqa: E501
            #   - https://github.com/streamlit/streamlit/blob/d07ffac8927e1a35b34684b55222854b3dd5a9a7/lib/streamlit/state/widgets.py#L258 # noqa: E501
            raise StreamlitSyncException(
                "Broken streamlit-sync library: Streamlit has most likely "
                "changed the widget id generation."
            )
        return match["user_key"]
    return widget_id


# Monkeypatch SessionState
if not getattr(SessionState, "_is_patched_by_streamlit_sync", False):

    def _always_set_frontend_value_if_changed(
        self: SessionState, widget_id: str, user_key: Optional[str]
    ) -> bool:
        """Keep `widget_state` and `session_state` in sync when a widget is registered.

        By default if a value has changed, the frontend widget will be updated only if
        it's a user-keyed-widget. I guess this is done because user-keyed-widget can
        be manually updated from st.session_state but not the "implicitly-keyed"
        widgets.

        In our case, we want to update the frontend for any value change.

        See:
            - Streamlit >= 1.8
                - https://github.com/streamlit/streamlit/blob/develop/lib/streamlit/state/session_state.py#L599 # noqa: E501
                - https://github.com/streamlit/streamlit/blob/d07ffac8927e1a35b34684b55222854b3dd5a9a7/lib/streamlit/state/session_state.py#L599 # noqa: E501

            - Streamlit <= 1.7
                - https://github.com/streamlit/streamlit/blob/1.7.0/lib/streamlit/state/session_state.py#L596 # noqa: E501
                - https://github.com/streamlit/streamlit/blob/a3f1cef8e23a97188710b71c4cf927f4783f58c5/lib/streamlit/state/session_state.py#L596 # noqa: E501
        """
        return self.is_new_state_value(user_key or widget_id)

    # For Streamlit >= 1.8
    initial_register_widget = getattr(SessionState, "register_widget", None)
    if initial_register_widget is not None:

        def _patched_register_widget(
            self: Any, metadata: Any, user_key: Optional[str]
        ) -> Tuple[Any, bool]:
            assert initial_register_widget is not None
            widget_value = initial_register_widget(self, metadata, user_key)
            return widget_value

        SessionState.register_widget = _patched_register_widget

    # For streamlit < 1.8
    SessionState.should_set_frontend_state_value = _always_set_frontend_value_if_changed

    # Patch only once
    SessionState._is_patched_by_streamlit_sync = True


def get_session_id() -> str:
    """Return current session id."""
    ctx = get_script_run_ctx()
    assert ctx is not None  # TODO: confirm this is true
    return ctx.session_id


def is_trigger_value(key: str, internal_session_state: SessionState) -> bool:
    """Return True if widget is a of type "trigger_value" (e.g. a button).

    We don't want to propagate the effect of the button to avoid performing twice the
    action.
    """
    widget_metadata = internal_session_state._new_widget_state.widget_metadata
    if key in widget_metadata:
        return widget_metadata[key].value_type == "trigger_value"
    return False


def is_form_submitter_value(key: str) -> bool:
    """Check if the widget key refers to a submit button from a form.

    In this case, value is not synced.

    Example: 'FormSubmitter:my_form-Submit'
    """
    return "FormSubmitter" in key and "-Submit" in key


def set_internal_values(mapping: Mapping[str, Any]) -> None:
    """Set values to the streamlit internal session state."""
    internal_state = get_session_state()
    for key, value in mapping.items():
        internal_state[widget_id_to_user_key(key)] = value


def del_internal_values(keys: Iterable[str]) -> None:
    """Delete values from the streamlit internal session state."""
    internal_state = get_session_state()
    for key in keys:
        del internal_state[widget_id_to_user_key(key)]
