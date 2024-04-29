# Import necessary libraries
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import streamlit as st
import os
import json

# functions 
import functools
from functions import get_stock_price

st.title("Mistral Chat")

# Function to reset the state
def reset_state():
    for key in st.session_state:
        del st.session_state[key]

# Section 1: API Key and Client Setup
# Get the API key from the environment variables or the user
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
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

# Move Section 2 and 3 to the sidebar
with st.sidebar:
    # Section 2: Model Selection
    # Initialize the model in session state if it's not already set
    if "mistral_model" not in st.session_state:
        st.session_state["mistral_model"] = 'mistral-large-latest'

    # Always display the dropdown
    model_options = ('open-mistral-7b', 'open-mixtral-8x22b', 'mistral-large-latest')
    st.session_state["mistral_model"] = st.selectbox('Select a model', model_options, index=model_options.index(st.session_state["mistral_model"]), key="model_select")

    # Section 3: System Prompt Input
    # Add system prompt input
    if "system_prompt" not in st.session_state:
        st.session_state["system_prompt"] = "You are a helpful assistant, providing accurate and relevant information to users while maintaining a neutral and respectful tone. Your responses should be concise and to the point, avoiding lengthy explanations unless necessary. You should not make assumptions about the user's personal beliefs or affiliations, and should strive to present information in an unbiased manner. Your goal is to assist the user to the best of your abilities, while maintaining a professional and helpful demeanor."
    st.text_area('System Prompt', value=st.session_state["system_prompt"], key="system_prompt")


# Section 4: Message Handling
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add system prompt as a ChatMessage if it doesn't exist
if st.session_state["system_prompt"] and not any(message.role == "system" for message in st.session_state.messages):
    st.session_state.messages.insert(0, ChatMessage(role="system", content=st.session_state["system_prompt"]))

# Display messages
for message in st.session_state.messages:
    if message.role != "system":  # Skip system messages for UI
        with st.chat_message(message.role):  # Use dot notation here
            st.markdown(message.content)  # And here
            
# Section 4.5: Set the tool use of our model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the price of any stock from Yahoo Finance",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "The ticker symbol of the stock"
                    }
                },
                "required": ["ticker"]
            }
        },
    },
]

names_to_functions = {
    "get_stock_price": functools.partial(get_stock_price, ticker="MSFT")
}

# Section 5: User Input and Response
client = MistralClient(api_key=api_key)
prompt = st.chat_input("What is up?")
if prompt:
    new_message = ChatMessage(role="user", content=prompt)
    st.session_state.messages.append(new_message)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat_stream(
            model=st.session_state["mistral_model"],
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto"
        ):
            print(response)
            if response.choices[0].delta.tool_calls is None:
                pass
            elif response.choices[0].delta.tool_calls:
                tool_call = response.choices[0].delta.tool_calls[0]
                function_name = tool_call.function.name
                function_params = json.loads(tool_call.function.arguments)

                # Execute the function
                function_result = names_to_functions[function_name](**function_params)

                # Append the function result as a new tool message
                st.session_state.messages.append(ChatMessage(role="tool", name=function_name, content=function_result))

                # Update the full_response with the function result
                full_response += function_result

                # Break the stream to process the next message with the function result
                break
            else:
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    # Append the assistant's response to the session state
    st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))
