import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from chatgpt_code_review.utils import remove_sidebar
from chatgpt_code_review import about

st.set_page_config(
    page_title="ChatGPT Code Review",
    page_icon="👋",
    initial_sidebar_state="collapsed"
)

remove_sidebar()

session_state = st.session_state

st.title("ChatGPT Code Review :rocket:")

with st.expander("About ChatGPT Code Review"):
    st.markdown(about.about_section, unsafe_allow_html=True)
    st.write("")

want_to_contribute = st.button("Review my code")
if want_to_contribute:
    switch_page("app")
