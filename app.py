import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import json
import openai
import os
import re
import chardet
from lida import Manager, TextGenerationConfig, llm
import matplotlib.pyplot as plt
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

lida = Manager(text_gen=llm("openai"))

textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=False)


def csv_agent_func(file_path, user_message):
    csv_agent = create_csv_agent(
        ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY),
        file_path,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        )
    
    try:
        tool_input = {
            "input": {
                "name": "python",
                "arguments": user_message
            }
        }
        response = csv_agent.run(tool_input)
        return response
    except Exception as e:
        st.write(f"Error: {e}")
        return None


def display_content_from_json(json_response):

    st.write(json_response)

    if "answer" in json_response:
        st.write(json_response["answer"])

    if "bar" in json_response:
        data = json_response["bar"]
        df = pd.DataFrame(data)
        df.set_index("cloums", inplace=True)
        st.bar_chart(df)

    if "table" in json_response:
        data =json_response["table"]
        df = pd.DataFrame(data["data"], colums=data['columns'])
        st.table(df)


def extract_code_from_response(response):
    """Extracts Python code from a string response."""
    # Use a regex pattern to match content between triple backticks
    code_pattern = r"```python(.*?)```"
    match = re.search(code_pattern, response, re.DOTALL)

    if match:
        return match.group(1).strip()
    
    return None


def csv_analyzer_app():
    """Main Streamlit application for CSV analysis."""
    
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:

        left_col, mid_col ,reight_col = st.columns([0.475, 0.05, 0.475])

        with left_col:
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
            st.subheader("File Information")
            st.write(file_details)
            
            
            # Save the uploaded file to disk
            file_path = os.path.join("/tmp", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Determine the encoding of the file
            rawdata = open(file_path, 'rb').read()
            result = chardet.detect(rawdata)
            encoding = result['encoding']
            
            st.subheader("Content Preview")
            df = pd.read_csv(file_path, encoding=encoding)
            st.dataframe(df)

            st.subheader("Suggestion")
            summary = lida.summarize(file_path, summary_method="default", textgen_config=textgen_config)
            goals = lida.goals(summary, n=5, textgen_config=textgen_config)
            for goal in goals:
                st.write(goal)
        
        with reight_col:
            st.subheader("Your Query")
            user_input = st.text_area("", height=100)
            if st.button("Submit"):
                response = csv_agent_func(file_path, user_input)
                
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

    

def xlsx_analyzer_app():

    uploaded_file = st.sidebar.file_uploader("Upload your file", type="xlsx")

    if uploaded_file is not None:
        left_col, mid_col ,reight_col = st.columns([0.475, 0.05, 0.475])

        with left_col: 
            file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
            st.subheader("File Information")
            st.write(file_details)

            file_path = os.path.join("/tmp", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            df = pd.read_excel(file_path)
            file_path_without_extension = os.path.splitext(file_path)[0]
            csv_file_path = file_path_without_extension + '.csv'
            df.to_csv(csv_file_path, index=False, encoding='utf-8')
            st.subheader("Content Preview")
            st.dataframe(df)

            st.subheader("Suggestion")
            summary = lida.summarize(csv_file_path, summary_method="default", textgen_config=textgen_config)
            goals = lida.goals(summary, n=5, textgen_config=textgen_config)
            for goal in goals:
                st.write(goal)

        with reight_col:
            st.subheader("Your Query")
            user_input = st.text_area("", height=100)
            if st.button("Submit"):
                response = csv_agent_func(csv_file_path, user_input)

                # Extracting code from the response
                code_to_execute = extract_code_from_response(response)

                if code_to_execute:
                    try:
                        st.write(code_to_execute)
                        # Making df available for execution in the context
                        exec(code_to_execute, globals(), {"df": df, "plt": plt})
                        fig = plt.gcf() # Get current figure
                        st.subheader("Visualization")
                        st.pyplot(fig) # Display
                        st.subheader("Detail Answer")
                        st.write(response)
                    except Exception as e:
                        st.write(f"Error executing code: {e}")
                else:
                    st.subheader("Detail Answer")
                    st.write(response)

def main():
    st.set_page_config(layout="wide")
    st.title('Ask Your Data')

    file_type = st.sidebar.selectbox("Choose a file type", ["csv", "xlsx"])
    
    if file_type == 'csv':
        csv_analyzer_app()
    elif file_type == 'xlsx':
        xlsx_analyzer_app()

    st.divider()

if __name__ == "__main__":
    main()
