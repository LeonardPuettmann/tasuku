# Import necessary libraries
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from PIL import Image
import streamlit as st
import os
import json

# functions 
import functools
from tools import get_stock_price, bing_search, save_todo, read_todos

# Function to reset the state
def reset_state():
    for key in st.session_state:
        del st.session_state[key]


im = Image.open("./images/favicon.png")
st.set_page_config(
    page_title="Tasuku",
    page_icon=im,
    layout="centered",
)

with st.sidebar:
    st.title(":red[佑 Tasuku]")
    st.write('This chatbot is created using the Mistral AI models. Tasuku means "help" or "assist" in japanese.')
    # Section 1: API Key and Client Setup
    # Get the API key from the environment variables or the user
    api_key = os.getenv("MISTRAL_API_KEY")
    if api_key: 
        st.success('API key already provided!', icon='✅')
    elif not api_key:
        if "api_key" not in st.session_state:
            st.session_state["api_key"] = st.text_input("Enter your API key", type="password")
        api_key = st.session_state["api_key"]
    else:
        expected_password = os.getenv("PASSWORD")
        if expected_password:
            password = st.text_input("What's the secret password?", type="password")
            # Check if the entered key matches the expected password
            if password != expected_password:
                api_key = ''
                st.error("Unauthorized access.")
                reset_state()  # This line will reset the script
            else:
                api_key = os.getenv("MISTRAL_API_KEY")
    
    # Section 2: Model Selection
    # Initialize the model in session state if it's not already set
    st.subheader('Models and parameters')
    if "mistral_model" not in st.session_state:
        st.session_state["mistral_model"] = 'open-mistral-7b'

    # Always display the dropdown
    model_options = ('open-mistral-7b','open-mixtral-8x22b', 'mistral-small-latest', 'mistral-large-latest')
    st.session_state["mistral_model"] = st.selectbox('Select a model', model_options, index=model_options.index(st.session_state["mistral_model"]), key="model_select")

    # Section 3: System Prompt Input
    # Add system prompt input
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = "You are a helpful assistant called Tasuku (佑). Your job is to be helpful and wait for users instructions. Keep your answer short. Do NOT mention your capabilties or tool use unless the user asks for it. Do NOT generate any commands yourself."
    st.text_area('System Prompt', value=st.session_state["system_prompt"], key="system_prompt")
    
    # Model settings
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_tokens = st.sidebar.slider('max_length', min_value=32, max_value=32000, value=1024, step=100)

    st.subheader('Available tools')
    st.markdown(
    """
    - Web search via Bing
    - Stock prices via Yahoo
    """
    )

# Section 4: Message Handling
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add system prompt as a ChatMessage if it doesn't exist
if st.session_state["system_prompt"] and not any(message.role == "system" for message in st.session_state.messages):
    st.session_state.messages.insert(0, ChatMessage(role="system", content=st.session_state["system_prompt"]))

# Display messages
avatar_paths = {"user": "./images/user.ico", "assistant": "./images/robot.ico"}
for message in st.session_state.messages:
    if message.role != "system":
        with st.chat_message(message.role, avatar=avatar_paths.get(message.role)):
            st.markdown(message.content)
            
# Section 4.5: Set the tool use of our model
with open('tools.json') as f:
    tools = json.load(f)

names_to_functions = {
    "get_stock_price": functools.partial(get_stock_price),
    "bing_search": functools.partial(bing_search),
    "save_todo": functools.partial(save_todo),
    "read_todo": functools.partial(read_todos)
}

# Section 5: User Input and Response
client = MistralClient(api_key=api_key)
prompt = st.chat_input("Message me...")
if prompt:
    new_message = ChatMessage(role="user", content=prompt)
    st.session_state.messages.append(new_message)
    with st.chat_message("user", avatar="./images/user.ico"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="./images/robot.ico"):
        message_placeholder = st.empty()
        full_response = ""
        function_result = ""  # Initialize function_result to an empty string
        model_params = {
            "model": st.session_state["mistral_model"],
            "messages": st.session_state.messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
        if st.session_state["mistral_model"] != "open-mistral-7b":
            model_params["tools"] = tools
            model_params["tool_choice"] = "auto"

        while True:
            for response in client.chat_stream(**model_params):
                if response.choices[0].delta.tool_calls is None:
                    full_response += (response.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "|")
                elif response.choices[0].delta.tool_calls:
                    tool_call = response.choices[0].delta.tool_calls[0]
                    function_name = tool_call.function.name
                    function_params = json.loads(tool_call.function.arguments)

                    # Execute the function
                    function_result = names_to_functions[function_name](**function_params)

                    # Create a new user message with the function result
                    new_message = ChatMessage(role="user", content=function_result)
                    st.session_state.messages.append(new_message)

                    # Break the loop to restart the chat stream with the new message
                    break
            else:
                # If the loop wasn't broken, exit the while loop
                break

        # Only display the message if it's not a function result
        if not function_result in full_response:
            message_placeholder.markdown(full_response)

        # Remove the function result message from st.session_state.messages
        if function_result:
            st.session_state.messages = [message for message in st.session_state.messages if message.content != function_result]

    # Append the assistant's response to the session state
    st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))
    print(st.session_state.messages)