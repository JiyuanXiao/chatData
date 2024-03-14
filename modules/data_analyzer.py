import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from lida import Manager, TextGenerationConfig, llm
import utils.csv_cleaner as csv_cleaner
import utils.csv_agent as csv_agent
import utils.extract_code_from_response as extract_code_from_response
import utils.get_csv_encoding as get_csv_encoding
from utils.constants import FILE_TYPE, FILE_ID, FILE_INFO, FILE_PATH, FILE_PATH_CLEAN
from utils.constants import SUGGESTION_NUM, SUGGESTIONS, REFRESH
from utils.constants import ORIGINAL_DF, CLEANED_DF, CLEANNING_DETAIL


lida = Manager(text_gen=llm("openai"))

textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=False)


def data_analyzer(session_state):
    
    data_file_type = session_state[FILE_TYPE]
    suggestion_num = session_state[SUGGESTION_NUM]

    uploaded_file = st.sidebar.file_uploader("Upload your file", type=data_file_type)
    
    if uploaded_file is not None:

        # If file is changed, reload all the sections
        if FILE_ID not in session_state or session_state[FILE_ID] != uploaded_file.file_id:
            session_state.clear()
            session_state[FILE_ID] = uploaded_file.file_id
            session_state[FILE_TYPE] = data_file_type
            session_state[SUGGESTION_NUM] = suggestion_num

        left_col, mid_col ,reight_col = st.columns([0.475, 0.05, 0.475])

        with left_col:

            if FILE_INFO not in session_state:
                # Display file information
                file_info = {"FileName": uploaded_file.name, 
                                "FileType": uploaded_file.type, 
                                "FileSize": uploaded_file.size}
                session_state[FILE_INFO] = file_info
            st.subheader("File Information")
            st.write(session_state[FILE_INFO])
            
            if FILE_PATH not in session_state:
                # Save the uploaded file to disk
                os.makedirs("./data", exist_ok=True)
                file_path = os.path.join("./data", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                session_state[FILE_PATH] = file_path

            # Handling CSV file
            if data_file_type == "csv":
                # Display the content of CSV
                if ORIGINAL_DF not in session_state:
                    encoding = get_csv_encoding(session_state[FILE_PATH])
                    session_state[ORIGINAL_DF] = pd.read_csv(session_state[FILE_PATH], encoding=encoding)
                st.subheader("Original Content")
                st.dataframe(session_state[ORIGINAL_DF])

                # Clean data
                if FILE_PATH_CLEAN not in session_state:
                    session_state[FILE_PATH_CLEAN] = csv_cleaner(session_state)

                if CLEANED_DF not in session_state:
                    # Display the content of cleaned CSV
                    encoding = get_csv_encoding(session_state[FILE_PATH_CLEAN])
                    session_state[CLEANED_DF] = pd.read_csv(session_state[FILE_PATH_CLEAN], encoding=encoding)
                st.subheader("Cleaned Content")
                st.dataframe(session_state[CLEANED_DF])

            # Handling Excel file
            elif data_file_type == 'xlsx':
                # Display the content of Excel
                if ORIGINAL_DF not in session_state:
                    session_state[ORIGINAL_DF] = pd.read_excel(session_state[FILE_PATH])
                st.subheader("Original Content")
                st.dataframe(session_state[ORIGINAL_DF])

                # Convert Excel to CSV and save the CSV file to disk
                file_path_without_extension = os.path.splitext(session_state[FILE_PATH])[0]
                session_state[FILE_PATH] = file_path_without_extension + '.csv'
                session_state[ORIGINAL_DF].to_csv(session_state[FILE_PATH], index=False, encoding='utf-8')

                # Clean data
                if FILE_PATH_CLEAN not in session_state:
                    session_state[FILE_PATH_CLEAN] = csv_cleaner(session_state)

                if CLEANED_DF not in session_state:
                    # Display the content of cleaned CSV
                    encoding = get_csv_encoding(session_state[FILE_PATH_CLEAN])
                    session_state[CLEANED_DF] = pd.read_csv(session_state[FILE_PATH_CLEAN], encoding=encoding)
                st.subheader("Cleaned Content")
                st.dataframe(session_state[CLEANED_DF])

            # Generate suggestion queries
            if suggestion_num > 0:
                st.subheader("Suggestions")
                if SUGGESTIONS not in session_state:
                    summary = lida.summarize(session_state[FILE_PATH_CLEAN], summary_method="default", textgen_config=textgen_config)
                    session_state[SUGGESTIONS] = lida.goals(summary, n=suggestion_num, textgen_config=textgen_config)
                n = 1
                for suggestion in session_state[SUGGESTIONS]:
                    suggestion_dict = {
                        "Suggestion#": n,
                        "Question": suggestion.question,
                        "Reason": suggestion.rationale,
                        "Visualization Suggestion": suggestion.visualization
                    }
                    st.write(suggestion_dict)
                    n += 1
        
        with reight_col:
            st.subheader("Your Query")
            user_input = st.text_area("", height=100)
            if st.button("Submit"):
                response = csv_agent(session_state[FILE_PATH_CLEAN], user_input)
                
                # Extracting code from the response
                code_to_execute = extract_code_from_response(response)
                
                if code_to_execute:
                    try:
                        # Standardize the symbol used in headers (use "_")
                        session_state[CLEANED_DF].columns = session_state[CLEANED_DF].columns.str.replace('.', '_').str.replace('-', '_').str.replace(' ', '_')

                        # Making df available for execution in the context
                        exec(code_to_execute, globals(), {"df": session_state[CLEANED_DF], "plt": plt})

                        # Display visualization
                        fig = plt.gcf()  # Get current figure
                        st.subheader("Visualization")
                        st.pyplot(fig)  # Display using Streamlit

                        # Display the process of visualization (for debuging)
                        st.subheader("Detail Answer")
                        st.write(response)

                    except Exception as e:
                        st.write(f"Error executing code: {e}")
                else:
                    # display the answer of user query
                    st.subheader("Detail Answer")
                    st.write(response)
