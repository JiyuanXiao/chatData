import streamlit as st
import modules.data_analyzer as data_analyzer
                    

def main():
    st.set_page_config(layout="wide")
    st.title('Ask Your Data')

    file_type = st.sidebar.selectbox("Choose a file type", ["csv", "xlsx"])

    data_analyzer(file_type)

    st.divider()

if __name__ == "__main__":
    main()
