import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from lida import Manager, TextGenerationConfig, llm
import utils.csv_agent as csv_agent
import utils.extract_code_from_response as extract_code_from_response
import utils.get_csv_encoding as get_csv_encoding


lida = Manager(text_gen=llm("openai"))

textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=False)


def data_analyzer(data_file_type):
    
    uploaded_file = st.sidebar.file_uploader("Upload your file", type=data_file_type)
    
    if uploaded_file is not None:

        left_col, mid_col ,reight_col = st.columns([0.475, 0.05, 0.475])

        with left_col:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
            st.subheader("File Information")
            st.write(file_details)
            
            # Save the uploaded file to disk
            os.makedirs("./data", exist_ok=True)
            file_path = os.path.join("./data", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.subheader("Content Preview")
            if data_file_type == "csv":
                encoding = get_csv_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
                st.dataframe(df)
            elif data_file_type == 'xlsx':
                df = pd.read_excel(file_path)
                st.dataframe(df)
                file_path_without_extension = os.path.splitext(file_path)[0]
                file_path = file_path_without_extension + '.csv'
                df.to_csv(file_path, index=False, encoding='utf-8')


            st.subheader("Suggestion")
            summary = lida.summarize(file_path, summary_method="default", textgen_config=textgen_config)
            goals = lida.goals(summary, n=5, textgen_config=textgen_config)
            for goal in goals:
                st.write(goal)
        
        with reight_col:
            st.subheader("Your Query")
            user_input = st.text_area("", height=100)
            if st.button("Submit"):
                response = csv_agent(file_path, user_input)
                
                # Extracting code from the response
                code_to_execute = extract_code_from_response(response)
                
                if code_to_execute:
                    try:
                        # Making df available for execution in the context
                        df.columns = df.columns.str.replace('.', '_').str.replace('-', '_').str.replace(' ', '_')
                        exec(code_to_execute, globals(), {"df": df, "plt": plt})
                        fig = plt.gcf()  # Get current figure
                        st.subheader("Visualization")
                        st.pyplot(fig)  # Display using Streamlit
                        st.subheader("Detail Answer")
                        st.write(response)
                    except Exception as e:
                        st.write(f"Error executing code: {e}")
                else:
                    st.subheader("Detail Answer")
                    st.write(response)
