import openai
import os
from dotenv import load_dotenv
load_dotenv()
import re
import streamlit as st
import datetime as dt


if "seasonal_fruits" not in st.session_state:
    st.session_state["seasonal_fruits"] = []
if "seasonal_vegetables" not in st.session_state:
    st.session_state["seasonal_vegetables"] = []
if 'location' not in st.session_state:
    st.session_state['location'] = ''
if 'date' not in st.session_state:
    st.session_state['date'] = dt.datetime.today()
if 'fruits_dict' not in st.session_state:
    st.session_state['fruits_dict'] = {}
if 'vegetables_dict' not in st.session_state:
    st.session_state['vegetables_dict'] = {}
if "response" not in st.session_state:
    st.session_state["response"] = ""
if "radius_dict" not in st.session_state:
    st.session_state["radius_dict"] = {}


# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG")

def query_models(location, date, is_fruit):
    content_type = "fruits" if is_fruit else "vegetables"
    models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]

    for model in models:
        try:
            if model.startswith("gpt-3.5"):
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that helps users find seasonal produce in their area."},
                    {"role": "user", "content": f"List the {content_type} that would typically be in season in {location} on date {date}. The location {location} will either be in the format of a zip code or city and state. The list should be in the format of a python list, with each item in the list separated by a comma and a space. For example, ['apple', 'banana', 'orange']."},
                ]

                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    max_tokens=250,
                    temperature=0.5,
                    frequency_penalty=0.5,
                )
                st.session_state.response = response
                seasonal_produce = response.choices[0].message.content
        except:
            prompt = f"You are a helpful assistant that helps users find seasonal produce in their area. List the {content_type} that would typically be in season in {location} on date {date}. The location {location} will either be in the format of a zip code or city and state. The list should be in the format of a python list, with each item in the list separated by a comma and a space. For example, ['apple', 'banana', 'orange']."
            response = openai.Completion.create(
                model=model,
                prompt=prompt,
                max_tokens=250,
                temperature=0.5,
                frequency_penalty=0.5,
            )
            st.session_state.response = response
            seasonal_produce = response.choices[0].text

        pattern = r"\[([^\]]+)\]"
        match = re.search(pattern, seasonal_produce)

        if match:
            produce_list = match.group(1).replace("'", "").split(", ")
            return produce_list
        

def find_seasonal_fruits(location, date):
    fruits_list = query_models(location, date, True)
    st.session_state.seasonal_fruits = fruits_list
    st.session_state.fruits_dict[location] = fruits_list
    return fruits_list


def find_seasonal_vegetables(location, date):
    vegetables_list = query_models(location, date, False)
    st.session_state.seasonal_vegetables = vegetables_list
    st.session_state.vegetables_dict[location] = vegetables_list
    return vegetables_list