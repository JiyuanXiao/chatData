import streamlit as st
import modules.data_analyzer as data_analyzer
from utils.constants import SUGGESTION_NUM, FILE_TYPE, REFRESH, SUGGESTIONS
                    

def main():
    st.set_page_config(layout="wide")
    st.title('Ask Your Data')

    session_state = st.session_state

    # Indicator for cache clearing
    session_state[REFRESH] = False

    file_type = st.sidebar.selectbox("Choose a file type", ["csv", "xlsx"])

    # If change file type, reload all the sections
    if FILE_TYPE not in session_state or session_state[FILE_TYPE] != file_type:
        session_state[REFRESH] = True


    suggestions_num = st.sidebar.slider("Select the number of suggestion", 0, 10, 3)

    # If the suggestion number changed, reload the suggestion section
    if SUGGESTION_NUM not in session_state or session_state[SUGGESTION_NUM] != suggestions_num:
        session_state[SUGGESTION_NUM] = suggestions_num
        if SUGGESTIONS in session_state:
            del session_state[SUGGESTIONS]

    # Clear all sections' cache data
    if session_state[REFRESH]:
        session_state.clear()
        session_state[FILE_TYPE] = file_type
        session_state[SUGGESTION_NUM] = suggestions_num

    data_analyzer(session_state)

    st.divider()

if __name__ == "__main__":
    main()
