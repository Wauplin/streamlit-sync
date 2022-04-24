import streamlit as st

import streamlit_sync

# Cache dir is optional. If None is provided, sessions are synced in memory.
CACHE_DIR = "./.st_sync_cache"

st.sidebar.write(
    "Example app using streamlit-sync library. "
    "For more details, please visit https://github.com/Wauplin/streamlit-sync"
)

# This step is optional. You can also use a default room name common to all sessions..
room_name = streamlit_sync.select_room_widget(cache_dir=CACHE_DIR)

with streamlit_sync.sync(room_name=room_name, cache_dir=CACHE_DIR):
    # Sliders
    # Toy example from https://github.com/streamlit/streamlit#a-little-example
    st.header("Sliders")

    st.info(
        'Sliders, as any other "normal" widgets, can have their value synced with '
        "other sessions. It is also possible to explicitly not sync a widget."
    )

    st.subheader("Synced slider")
    y = st.slider("Select a value")
    st.write(y, "squared is", y * y)

    st.subheader("Synced slider using custom key widget.")
    x = st.slider("Select a value", key="key")
    st.write(x, "squared is", x * x)

    st.subheader("Not synced slider")
    x = st.slider("Select a value", key=streamlit_sync.get_not_synced_key("key"))
    st.write(x, "squared is", x * x)

    # Button
    st.header("Buttons")

    st.info(
        "Button action is never synced to avoid duplicate actions. "
        "However, if a value is updated in the session state, this update is synced "
        "with other sessions."
    )

    if st.session_state.get("NB_CLICKS") is None:
        st.session_state["NB_CLICKS"] = 0

    if st.button(label="click"):
        st.session_state["NB_CLICKS"] += 1

    st.write("Clicked **" + str(st.session_state["NB_CLICKS"]) + "** times !")

    # Form
    st.header("Form")

    st.info("Form data is synced only when submit button is clicked.")

    if st.session_state.get("guess") is None:
        st.session_state["guess"] = ""

    with st.form(key="my_form", clear_on_submit=True):
        answer = st.text_input("Make a guess")
        submit = st.form_submit_button(label="Submit")

    if submit:
        st.session_state["guess"] = answer

    st.write("Your guess: **" + str(st.session_state["guess"]) + "**")
