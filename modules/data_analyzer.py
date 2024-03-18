import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from lida import Manager, TextGenerationConfig, llm
import utils.csv_cleaner as csv_cleaner
import utils.csv_agent as csv_agent
import utils.extract_code_from_response as extract_code_from_response
import utils.get_csv_encoding as get_csv_encoding
import utils.constants as constants
import utils.texts as texts

lida = Manager(text_gen=llm(provider="openai"))

textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=False)

def data_analyzer(session_state, language):
    
    data_file_type = session_state[constants.FILE_TYPE]
    suggestion_num = session_state[constants.SUGGESTION_NUM]

    uploaded_file = st.sidebar.file_uploader(texts.prompt_file_upload[language], type=data_file_type)
    
    if uploaded_file is not None:

        # If file is changed, reload all the sections
        if constants.FILE_ID not in session_state or session_state[constants.FILE_ID] != uploaded_file.file_id:
            session_state.clear()
            session_state[constants.FILE_ID] = uploaded_file.file_id
            session_state[constants.FILE_TYPE] = data_file_type
            session_state[constants.SUGGESTION_NUM] = suggestion_num

        left_col, mid_col ,reight_col = st.columns([0.475, 0.05, 0.475])

        with left_col:

            if constants.FILE_INFO not in session_state:
                # Display file information
                file_info = {texts.file_info_name[language]: uploaded_file.name, 
                                texts.file_info_type[language]: uploaded_file.type, 
                                texts.file_info_size[language]: uploaded_file.size}
                session_state[constants.FILE_INFO] = file_info
            st.subheader(texts.section_header_file_info[language])
            st.write(session_state[constants.FILE_INFO])
            
            if constants.FILE_PATH not in session_state:
                # Save the uploaded file to disk
                os.makedirs("./data", exist_ok=True)
                file_path = os.path.join("./data", uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                session_state[constants.FILE_PATH] = file_path

            # Handling CSV file
            if data_file_type == "csv":
                # Display the content of CSV
                if constants.ORIGINAL_DF not in session_state:
                    encoding = get_csv_encoding(session_state[constants.FILE_PATH])
                    session_state[constants.ORIGINAL_DF] = pd.read_csv(session_state[constants.FILE_PATH], encoding=encoding)
                st.subheader(texts.section_header_original_data[language])
                st.dataframe(session_state[constants.ORIGINAL_DF])

                # Clean data
                if constants.FILE_PATH_CLEAN not in session_state:
                    session_state[constants.FILE_PATH_CLEAN] = csv_cleaner(session_state)

                if constants.CLEANED_DF not in session_state:
                    # Display the content of cleaned CSV
                    encoding = get_csv_encoding(session_state[constants.FILE_PATH_CLEAN])
                    session_state[constants.CLEANED_DF] = pd.read_csv(session_state[constants.FILE_PATH_CLEAN], encoding=encoding)
                st.subheader(texts.section_header_cleaned_data[language])
                st.dataframe(session_state[constants.CLEANED_DF])

                if constants.CLEANNING_DETAIL in session_state:
                    st.subheader(texts.section_header_cleannig_detail[language])
                    st.write(session_state[constants.CLEANNING_DETAIL])

            # Handling Excel file
            elif data_file_type == 'xlsx':
                # Display the content of Excel
                if constants.ORIGINAL_DF not in session_state:
                    session_state[constants.ORIGINAL_DF] = pd.read_excel(session_state[constants.FILE_PATH])
                st.subheader(texts.section_header_original_data[language])
                st.dataframe(session_state[constants.ORIGINAL_DF])

                # Convert Excel to CSV and save the CSV file to disk
                file_path_without_extension = os.path.splitext(session_state[constants.FILE_PATH])[0]
                session_state[constants.FILE_PATH] = file_path_without_extension + '.csv'
                session_state[constants.ORIGINAL_DF].to_csv(session_state[constants.FILE_PATH], index=False, encoding='utf-8')

                # Clean data
                if constants.FILE_PATH_CLEAN not in session_state:
                    session_state[constants.FILE_PATH_CLEAN] = csv_cleaner(session_state)

                if constants.CLEANED_DF not in session_state:
                    # Display the content of cleaned CSV
                    encoding = get_csv_encoding(session_state[constants.FILE_PATH_CLEAN])
                    session_state[constants.CLEANED_DF] = pd.read_csv(session_state[constants.FILE_PATH_CLEAN], encoding=encoding)
                st.subheader(texts.section_header_cleaned_data[language])
                st.dataframe(session_state[constants.CLEANED_DF])

                if constants.CLEANNING_DETAIL in session_state:
                    st.subheader(texts.section_header_cleannig_detail[language])
                    st.write(session_state[constants.CLEANNING_DETAIL])

            # Generate suggestion queries
            if suggestion_num > 0:
                try:
                    st.subheader(texts.section_header_suggestion[language])
                    if constants.SUGGESTIONS not in session_state:
                        summary = lida.summarize(session_state[constants.FILE_PATH_CLEAN], summary_method="default", textgen_config=textgen_config)
                        st.write(summary)
                        session_state[constants.SUGGESTIONS] = lida.goals(summary, n=suggestion_num, textgen_config=textgen_config)
                except Exception as e:
                    st.warning(f"{texts.error[language]}: {e}")
                else:
                    n = 1
                    for suggestion in session_state[constants.SUGGESTIONS]:
                        suggestion_dict = {
                            "Suggestion#": n,
                            "Question": suggestion.question,
                            "Reason": suggestion.rationale,
                            "Visualization Suggestion": suggestion.visualization
                        }
                        st.write(suggestion_dict)
                        n += 1
        
        with reight_col:
            st.subheader(texts.section_header_query[language])
            query_type = st.radio(texts.prompt_answer_type[language], [texts.answer_type_text[language], texts.answer_type_visual[language]])
            user_input = st.text_area("", height=100)
            if query_type == texts.answer_type_visual[language]:
                visualize_prompt_header = "Please generate python script to visualize the statement or question below: \n\n```\n"
                visualize_prompt_tailer = "\n```\n\n You MUST generate PYTHON SCRIPT in your answer. Please use the EXACTLY SAME PROPERTY NAMES as the datasets' in the script."
                user_input = visualize_prompt_header + user_input
                user_input = user_input + visualize_prompt_tailer
            elif query_type == texts.answer_type_text[language]:
                visualize_prompt_header = "Please generate plain text content to demonstrate the statment or answer the question below. Here is the question: \n\n```\n"
                visualize_prompt_tailer = f"\n```\n\n You MUST generate the PLAIN TEXT answer based on the dataset. Just tell the reason if the dataset doesn't have enought information to derive an accurate demonstration or answer. Plase don't makeup an answer if you can't derive an accurate answer. You MUST generate the answer IN {texts.language[language]}."
                user_input = visualize_prompt_header + user_input
                user_input = user_input + visualize_prompt_tailer
            if st.button(texts.button_submit[language]):
                response = csv_agent(session_state[constants.FILE_PATH_CLEAN], user_input)
                
                # Extracting code from the response
                code_to_execute = extract_code_from_response(response)
                
                if code_to_execute:
                    try:
                        # Standardize the symbol used in headers (use "_")
                        #session_state[CLEANED_DF].columns = session_state[CLEANED_DF].columns.str.replace('.', '_').str.replace('-', '_').str.replace(' ', '_')

                        # Making df available for execution in the context
                        df_copy = session_state[constants.CLEANED_DF].copy()
                        exec(code_to_execute, globals(), {"df": df_copy, "plt": plt})

                        # Display visualization
                        fig = plt.gcf()  # Get current figure
                        st.subheader(texts.section_header_visualization[language])
                        st.pyplot(fig)  # Display using Streamlit

                        # Display the process of visualization (for debuging)
                        st.subheader(texts.section_header_answer[language])
                        st.write(response)

                    except Exception as e:
                        st.write(f"{texts.error[language]}: {e}")
                        st.write(response)
                else:
                    # display the answer of user query
                    st.subheader(texts.section_header_answer[language])
                    st.write(response)
