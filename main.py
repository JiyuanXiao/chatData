import streamlit as st

def main():
    st.set_page_config(page_title="Analyze your CVS")
    st.header("Analyze your CVS")

    user_csv = st.file_uploader("Upload your CSV file", type="csv")
    

if __name__ == "__main__":
    main()