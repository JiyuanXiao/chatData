import streamlit as st
import modules.data_analyzer as data_analyzer
                    

def main():
    st.set_page_config(layout="wide")
    st.title('Ask Your Data')

    file_type = st.sidebar.selectbox("Choose a file type", ["csv", "xlsx"])

    suggestions_num = st.sidebar.slider("Select the number of suggestion", 0, 10, 3)

    data_analyzer(file_type, suggestions_num)

    st.divider()

if __name__ == "__main__":
    main()
