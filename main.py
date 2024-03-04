import streamlit as st
from lida import Manager, TextGenerationConfig, llm
from dotenv import load_dotenv
import os
import openai
import io
from PIL import Image
from io import BytesIO
import base64


#def main():
#    st.set_page_config(page_title="Analyze your CVS")
#    st.header("Analyze your CVS")

#    user_csv = st.file_uploader("Upload your CSV file", type="csv")
    

#if __name__ == "__main__":
#    main()


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def base64_to_image(base64_string):
    # Decode the base64 string
    byte_data = base64.b64decode(base64_string)

    # Use BytesIO to convert the byte data to image
    return Image.open(BytesIO(byte_data))

lida = Manager(text_gen=llm("openai"))

textgen_config = TextGenerationConfig(n=1, temperature=0.5, model="gpt-3.5-turbo", use_cache=False)

menu = st.sidebar.selectbox("Choose an option", ["Visualize Your Data", "Ask Your Data"])

if menu == "Visualize Your Data":
    st.subheader("Visualize Your Data")
    file_uploader = st.file_uploader("Upload your CSV file", type="csv")

    if file_uploader is not None:
        data_filename = "data.csv"
        with open(data_filename, "wb")as f:
            f.write(file_uploader.getvalue())
        summary = lida.summarize(data_filename, summary_method="default", textgen_config=textgen_config)
        #st.write(summary)
        goals = lida.goals(summary, n=5, textgen_config=textgen_config)
        for goal in goals:
            st.write(goal)

    user_query = st.text_area("Ask your data to generate Graph", height=200)
    if st.button("Generate Graph"):
        if len(user_query) > 0:
            st.info("Your query: " + user_query)
            #lida = Manager(text_gen=llm("openai"))
            #textgen_config = TextGenerationConfig(n=1, temperature=0, use_cache=False)
            summary = lida.summarize("data.csv", summary_method="default", textgen_config=textgen_config)
            charts = lida.visualize(summary, goal=user_query, textgen_config=textgen_config)
            if len(charts)>0:
                img_base64 = charts[0].raster
                img = base64_to_image(img_base64)
                st.image(img) 
            else:
                st.warning("Fail to Resolve your Query")

elif menu == "Ask Your Data":
    st.info("Coming Soon")               
