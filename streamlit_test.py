import streamlit as st
import requests

# Set up the URL of your FastAPI server
url = "http://localhost:8000"

# Define a function to get the session ID
@st.cache(allow_output_mutation=True)
def get_session_id():
    return {"session_id": None}

# Define a function to make a POST request to the server
def make_post_request(endpoint, data):
    session_id = get_session_id()
    headers = {"session_id": session_id["session_id"]} if session_id["session_id"] else {}
    response = requests.post(f"{url}/{endpoint}", headers=headers, params=data)
    
    if 'session_id' in response.headers:
        session_id["session_id"] = response.headers["session_id"]
        
    return response.json()

# Start the Streamlit app
def main():
    st.title("Chat App")

    # Text input field
    text_input = st.text_input("Type your message here")

    # Buttons to send a user message, initialize chat, add a chef message, get a chef response, view chat history and clear chat history.
    if st.button("Send User Message"):
        response = make_post_request("add_user_message", {"message": text_input})
        st.write(response)
    context = st.text_input("Type your context here")
    initial_message = st.text_input("Type your initial message here")
    if st.button("Initialize Chat"):
        response = make_post_request("initialize_chat", {"context": context, "recipe_text": initial_message})
        st.write(response)

    if st.button("Send Chef Message"):
        response = make_post_request("add_chef_message", {"message": text_input})
        st.write(response)
    question = st.text_input("Type your question here")
    if st.button("Get Chef Response"):
        response = make_post_request("get_chef_response", {"question": question})
        st.write(response)

    if st.button("View Chat History"):
        response = make_post_request("view_chat_history", {})
        st.write(response)

    if st.button("Clear Chat History"):
        response = make_post_request("clear_chat_history", {})
        st.write(response)

# Run the app
if __name__ == "__main__":
    main()
