import os

from chatgpt_code_review import about
from chatgpt_code_review import display
from chatgpt_code_review import download
from chatgpt_code_review import forms
from chatgpt_code_review import query
from chatgpt_code_review import repo
import streamlit as st
from chatgpt_code_review import utils
from chatgpt_code_review.utils import remove_sidebar
from streamlit_extras.switch_page_button import switch_page

env_file_path = ".env"
log_file = "app.log"


temp_dir = "./tmp/chatgpt-code-review"

session_state = st.session_state

def app():
    utils.load_environment_variables(env_file_path)
    utils.set_environment_variables()
    utils.configure_logging(log_file)

    # The temp dir context + temp_dir is needed to temporarely clone the github repository and access the content
    # This solution is worse from the downloading point of view, but theoretically allows for direct push to github
    # without going crazy
    with utils.TempDirContext(temp_dir):
        st.set_page_config(
            page_title="ChatGPT Code Review",
            initial_sidebar_state="collapsed"
        )

        remove_sidebar()

        st.title("Insert credentials 🐱‍💻")

        repo_form = forms.RepoForm()
        with st.form("repo_url_form"):
            repo_form.display_form()

        if 'submitted_form' not in session_state:
            print('Initializing session state')
            session_state['submitted_form'] = False

        # Explanation of the code:
        # This section ensures that the code does not proceed if the 'clone_repo_button' is not clicked.
        # Streamlit will still execute the code below, but the data from GitHub won't be rendered or loaded.
        # When the button is clicked, its value becomes True, indicating that data should be loaded.
        # However, if the URL or API key are not valid, the code will break.
        # In such a case, 'st.stop()' is triggered, and the code stops execution.
        if session_state['submitted_form'] and not repo_form.is_github_repo_valid() and not repo_form.is_api_key_valid():
            st.stop()

        # So the trick is to add if statements to the variable to avoid the reset because of streamlit rerunning code
        # TODO: Please find a better way to do this it's horrible. Probavbly there's some hidden catch to manage this
        #  streamoit behaviour
        if 'valid_credentials' not in session_state:
            print('Initializing session state')
            session_state['valid_credentials'] = False

        if 'overall_review' not in session_state:
            print('Initializing overall review')
            session_state['overall_review'] = False

        # Streamlit re-runs the whole code, so once I create the buttons I have no way of clicking them because
        # this condition is dependent on the other button, that will be reset after i click it.
        # TODO: find the best way to implement this
        if session_state['submitted_form'] and repo_form.is_github_repo_valid() and repo_form.is_api_key_valid():
            ad_hoc_review = st.button("AD-hoc review on selected code")
            overall_review = st.button("Overall review", on_click=lambda: st.session_state.update({'overall_review': True}))
            print('Inside positive submitted form')
            session_state['valid_credentials'] = True

        print('valid credentials outside:', session_state['valid_credentials'])
        print('overall_review outside:', session_state['overall_review'])
        if session_state['valid_credentials'] and session_state['overall_review']:
            print("AOOOOOOOOO DAI CHE E' VALIDO")
            switch_page("overall_review")

        # if session_state['valid_credentials'] and session_state['ad_hoc_review']:
        #     print("AOOOOOOOOO DAI CHE E' AD HOC")
        #     # switch_page("overall_review")

        # repo_url, extensions = repo_form.get_form_data()
        #
        # analyze_files_form = forms.AnalyzeFilesForm(session_state)
        # with st.form("analyze_files_form"):
        #     print("Dentro l'analyze form")
        #     if repo_form.clone_repo_button or session_state.get("code_files"):
        #         if not session_state.get("code_files"):
        #             session_state.code_files = (
        #                 repo.list_code_files_in_repository(
        #                     repo_url, extensions
        #                 )
        #             )
        #
        #         analyze_files_form.display_form()
        #
        # # Analyze the selected files
        # with st.spinner("Analyzing files..."):
        #     print("Dentro lo spinner")
        #     if session_state.get("analyze_files"):
        #         if session_state.get("selected_files"):
        #             recommendations = query.analyze_code_files(
        #                 session_state.selected_files
        #             )
        #
        #             # Display the recommendations
        #             st.header("Recommendations")
        #             first = True
        #             recommendation_list = []
        #             for rec in recommendations:
        #                 if not first:
        #                     st.write("---")
        #                 else:
        #                     first = False
        #                 st.subheader(display.escape_markdown(rec["code_file"]))
        #                 recommendation = (
        #                     rec["recommendation"] or "No recommendations"
        #                 )
        #                 st.markdown(recommendation)
        #                 with st.expander("View Code"):
        #                     extension = os.path.splitext(rec["code_file"])[1]
        #                     display.display_code(
        #                         rec["code_snippet"], extension
        #                     )
        #                 recommendation_list.append(rec)
        #             if recommendation_list:
        #                 session_state.recommendation_list = recommendation_list
        #         else:
        #             st.error("Please select at least one file to analyze.")
        #             st.stop()
        #
        # st.write("")
        #
        # download.download_markdown(session_state.get("recommendation_list"))


if __name__ == "__main__":
    app()
