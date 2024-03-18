import streamlit as st
import modules.data_analyzer as data_analyzer
import utils.constants as constants
import utils.texts as texts
                    

def main():
    st.set_page_config(layout="wide")

    session_state = st.session_state

    language = st.sidebar.selectbox("Choose a language", ["English", "简体中文"])

    st.title(texts.title[language])

    # Indicator for cache clearing
    session_state[constants.REFRESH] = False

    file_type = st.sidebar.radio(texts.prompt_file_type[language], ["xlsx", "csv"])

    # If change file type, reload all the sections
    if constants.FILE_TYPE not in session_state or session_state[constants.FILE_TYPE] != file_type:
        session_state[constants.REFRESH] = True


    #suggestions_num = st.sidebar.slider("Select the number of suggestion", 0, 10, 3)
    suggestions_num = 0

    # If the suggestion number changed, reload the suggestion section
    if constants.SUGGESTION_NUM not in session_state or session_state[constants.SUGGESTION_NUM] != suggestions_num:
        session_state[constants.SUGGESTION_NUM] = suggestions_num
        if constants.SUGGESTIONS in session_state:
            del session_state[constants.SUGGESTIONS]

    # Clear all sections' cache data
    if session_state[constants.REFRESH]:
        session_state.clear()
        session_state[constants.FILE_TYPE] = file_type
        session_state[constants.SUGGESTION_NUM] = suggestions_num

    data_analyzer(session_state, language)

    st.divider()

if __name__ == "__main__":
    main()
