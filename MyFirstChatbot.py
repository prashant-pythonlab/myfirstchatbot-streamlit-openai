# Import Libraries

import openai
import streamlit as st
from streamlit_chat import message
import tempfile
import base64
from docx_parser import DocumentParser
import pathlib
import time
import os


# Open API key
openai.api_key = st.secrets["OPEN_API_KEY"]

# Creating the chatbot interfaces
st.header("My First Chatbot")
st.subheader("Using :red[Streamlit] + :green[OpenAI]")
st.caption("🤖Input text or upload a file and let me analyze it!")

#set backgroud
@st.cache_data()
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file) 
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: scroll; # doesn't work
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

set_png_as_page_bg(os.path.join(os.getcwd() , "background.png"))

# Storing the input
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
else:
    # display the existing  chat messages
    for message in st.session_state.messages:
        with st.chat_message(name=message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])

# Creating a function that returns the user's input from a text input field
def get_text():
    input_text = st.chat_input( key = "input", placeholder="Input Text")
    return input_text

uploaded_filename=""
def get_file_uploaded():
    global uploaded_filename
    with st.sidebar:
        uploaded_file = st.file_uploader("Upload a file to get help from assistant!", type=['txt','docx'])
        if uploaded_file is not None:             
            uploaded_filename = uploaded_file.name
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            file_suffix=pathlib.Path(uploaded_filename).suffix
            data=""
            if file_suffix == '.docx':
                doc = DocumentParser(tmp_file_path)
                for _type, item in doc.parse():
                    print(_type, item)
                    data += item['text'] + '\n'
            else:
                with open(tmp_file_path, 'r') as f:
                    data = f.read()
            return data

#set avatars
user_avatar="😎"
assistant_avatar="🤖"

# We will get text from text window or uploaded file and store in separate dictionaries
fileuploaded_input = {"type": "file", "data": get_file_uploaded()}
text_input = {"type": "text", "data": get_text()}

user_input = text_input if text_input.get('data') is not None else fileuploaded_input
if user_input['data']:
    input_type = user_input['type']
    input_content = user_input['data']

    # Store the input    
    if input_type == 'text':
        with st.chat_message("user", avatar=user_avatar):
            st.markdown(input_content)
    st.session_state.messages.append({"role": "user", "avatar": user_avatar, "content": input_content})

    # generate response from openai
    with st.chat_message("assistant", avatar=assistant_avatar):
        if input_type == 'file':
            with st.spinner(f"I have detected a file {uploaded_filename}. Analyzing file content..."):
                time.sleep(2)
                st.markdown("Here is the file content .. ")
                st.markdown(input_content)
        full_response = ""
        message_placeholder= st.empty()
        for response in openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
                ],
            stream=True
        ):
            full_response  += response.choices[0].delta.get("content","")
            message_placeholder.markdown(full_response + '▌')
        message_placeholder.markdown(full_response)
        st.markdown("Can I assist you in any other way on this query text?")
    st.session_state.messages.append({"role": "assistant", "avatar": assistant_avatar, "content": full_response})









