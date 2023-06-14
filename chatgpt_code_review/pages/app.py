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

env_file_path = ".env"
log_file = "app.log"


temp_dir = "./tmp/chatgpt-code-review"


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

        session_state = st.session_state

        st.title("ChatGPT Code Review :rocket:")

        with st.expander("About ChatGPT Code Review"):
            st.markdown(about.about_section, unsafe_allow_html=True)
            st.write("")

        repo_form = forms.RepoForm()
        with st.form("repo_url_form"):
            repo_form.display_form()

        # Check if the API key is valid before proceeding
        if repo_form.clone_repo_button and not (repo_form.is_github_repo_valid() and repo_form.is_api_key_valid()):
            st.stop()

        repo_url, extensions = repo_form.get_form_data()

        analyze_files_form = forms.AnalyzeFilesForm(session_state)
        with st.form("analyze_files_form"):
            if repo_form.clone_repo_button or session_state.get("code_files"):
                if not session_state.get("code_files"):
                    session_state.code_files = (
                        repo.list_code_files_in_repository(
                            repo_url, extensions
                        )
                    )

                analyze_files_form.display_form()

        # Analyze the selected files
        with st.spinner("Analyzing files..."):
            if session_state.get("analyze_files"):
                if session_state.get("selected_files"):
                    recommendations = query.analyze_code_files(
                        session_state.selected_files
                    )

                    # Display the recommendations
                    st.header("Recommendations")
                    first = True
                    recommendation_list = []
                    for rec in recommendations:
                        if not first:
                            st.write("---")
                        else:
                            first = False
                        st.subheader(display.escape_markdown(rec["code_file"]))
                        recommendation = (
                            rec["recommendation"] or "No recommendations"
                        )
                        st.markdown(recommendation)
                        with st.expander("View Code"):
                            extension = os.path.splitext(rec["code_file"])[1]
                            display.display_code(
                                rec["code_snippet"], extension
                            )
                        recommendation_list.append(rec)
                    if recommendation_list:
                        session_state.recommendation_list = recommendation_list
                else:
                    st.error("Please select at least one file to analyze.")
                    st.stop()

        st.write("")

        download.download_markdown(session_state.get("recommendation_list"))


if __name__ == "__main__":
    app()
