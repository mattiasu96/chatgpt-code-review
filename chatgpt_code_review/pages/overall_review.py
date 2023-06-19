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

def overall_review():

    analyze_files_form = forms.AnalyzeFilesForm(session_state)
    with st.form("analyze_files_form"):
        print("Dentro l'analyze form")
        if session_state['submitted_form'] or session_state.get("code_files"):
            print("printing repo url:", session_state['repo_url'])
            if not session_state.get("code_files"):
                session_state.code_files = (
                    repo.list_code_files_in_repository(
                        session_state['repo_url'], session_state['extensions']
                    )
                )

            analyze_files_form.display_form()

    # Analyze the selected files
    with st.spinner("Analyzing files..."):
        print("Dentro lo spinner")
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
    overall_review()