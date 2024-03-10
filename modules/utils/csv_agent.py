import streamlit as st
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def csv_agent(file_path, user_message):
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