import os
import pandas as pd
import streamlit as st
import utils.csv_agent as csv_agent
import utils.get_csv_encoding as get_csv_encoding
import utils.extract_code_from_response as extract_code_from_response
from utils.constants import FILE_PATH, CLEANNING_DETAIL

DATA_CLEANNING_PROMPT_HEADER = "Data cleaning steps will be specified below: "
DTAT_CLEANNING_PROMPT_REQUIREMENTS =[ "1. rename all column property so that it repersents the meaning of the data",
                                     "2. remove all rows which are not the data (such as title, summary, and column name)", 
                                     "3. translate and replace the columns name to English"]
DTAT_CLEANNING_PROMPT_ACTION = "Generate python script to implement the cleanning steps above step by step, and strickly follow the order."
DATA_CLEANNING_PROMPT_ORIGIN_FILE = "The original file is "
DATA_CLEANNING_PROMPT_CLEANED_FILE = 'Save the cleaned data to: '

def csv_cleaner(session_state):
    file_path = session_state[FILE_PATH]
    data_cleanning_prompt = DATA_CLEANNING_PROMPT_HEADER
    for requirment in DTAT_CLEANNING_PROMPT_REQUIREMENTS:
        data_cleanning_prompt += requirment
    data_cleanning_prompt += DTAT_CLEANNING_PROMPT_ACTION
    data_cleanning_prompt += DATA_CLEANNING_PROMPT_ORIGIN_FILE
    data_cleanning_prompt += file_path
    data_cleanning_prompt += DATA_CLEANNING_PROMPT_CLEANED_FILE

    file_name, file_extesion = os.path.splitext(file_path)
    cleaned_file_name = file_name + "_cleaned"
    cleaned_file_path = cleaned_file_name + file_extesion

    data_cleanning_prompt += cleaned_file_path

    print(data_cleanning_prompt)

    if CLEANNING_DETAIL not in session_state:
        session_state[CLEANNING_DETAIL] = csv_agent(file_path, data_cleanning_prompt)

    cleanning_code = extract_code_from_response(session_state[CLEANNING_DETAIL])

    st.subheader("Data Cleanning")
    if cleanning_code:
        st.write(session_state[CLEANNING_DETAIL])
        encoding = get_csv_encoding(file_path)
        df = pd.read_csv(file_path, encoding=encoding)
        exec(cleanning_code, globals(), {"df": df})
        return cleaned_file_path

    
    st.write("Dataset looks good! No needs for cleanning...")
    return file_path