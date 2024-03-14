import streamlit as st
import pandas as pd
import openpyxl
import matplotlib.pyplot as plt
import os
from lida import Manager, TextGenerationConfig, llm
import utils.csv_cleaner as csv_cleaner
import utils.csv_agent as csv_agent
import utils.extract_code_from_response as extract_code_from_response
import utils.get_csv_encoding as get_csv_encoding


lida = Manager(text_gen=llm("openai"))

textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=False)


def data_analyzer(data_file_type, suggestion_num):
    
    uploaded_file = st.sidebar.file_uploader("Upload your file", type=data_file_type)
    
    if uploaded_file is not None:

        left_col, mid_col ,reight_col = st.columns([0.475, 0.05, 0.475])

        with left_col:

            # Display file information
            file_info = {"FileName": uploaded_file.name, 
                            "FileType": uploaded_file.type, 
                            "FileSize": uploaded_file.size}
            st.subheader("File Information")
            st.write(file_info)
            
            # Save the uploaded file to disk
            os.makedirs("./data", exist_ok=True)
            file_path = os.path.join("./data", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Handling CSV file
            if data_file_type == "csv":
                # Display the content of CSV
                encoding = get_csv_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
                st.subheader("Original Content")
                st.dataframe(df)

                # Clean data
                file_path = csv_cleaner(file_path)

                # Display the content of cleaned CSV
                encoding = get_csv_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
                st.subheader("Cleaned Content")
                st.dataframe(df)

            # Handling Excel file
            elif data_file_type == 'xlsx':
                # Display the content of Excel
                df = pd.read_excel(file_path)
                st.subheader("Original Content")
                st.dataframe(df)

                # Convert Excel to CSV and save the CSV file to disk
                file_path_without_extension = os.path.splitext(file_path)[0]
                file_path = file_path_without_extension + '.csv'
                df.to_csv(file_path, index=False, encoding='utf-8')

                # Clean data
                file_path = csv_cleaner(file_path)

                # Display the content of cleaned CSV
                encoding = get_csv_encoding(file_path)
                df = pd.read_csv(file_path, encoding=encoding)
                st.subheader("Cleaned Content")
                st.dataframe(df)

            # Generate suggestion queries
            if suggestion_num > 0:
                st.subheader("Suggestion")
                summary = lida.summarize(file_path, summary_method="default", textgen_config=textgen_config)
                goals = lida.goals(summary, n=suggestion_num, textgen_config=textgen_config)
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
                        # Standardize the symbol used in headers (use "_")
                        df.columns = df.columns.str.replace('.', '_').str.replace('-', '_').str.replace(' ', '_')

                        # Making df available for execution in the context
                        exec(code_to_execute, globals(), {"df": df, "plt": plt})

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
