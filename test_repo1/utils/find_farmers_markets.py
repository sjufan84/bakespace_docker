import streamlit as st
import googlemaps
import folium
import os
from streamlit_folium import folium_static
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_KEY")
gmaps = googlemaps.Client(key=api_key)

if 'markets' not in st.session_state:
    st.session_state['markets'] = {}
if 'location' not in st.session_state:
    st.session_state['location'] = ''
if 'maps' not in st.session_state:
    st.session_state['maps'] = {}
if 'radius_dict' not in st.session_state:
    st.session_state['radius_dict'] = {}

def get_center_and_bounds(markets):
    latitudes = [market["location"]["lat"] for market in markets]
    longitudes = [market["location"]["lng"] for market in markets]

    center_lat = (max(latitudes) + min(latitudes)) / 2
    center_lng = (max(longitudes) + min(longitudes)) / 2

    bounds = [(min(latitudes), min(longitudes)), (max(latitudes), max(longitudes))]
    center_location = [center_lat, center_lng]

    return center_location, bounds


def miles_to_meters(miles):
    return miles * 1609.34


def get_farmers_markets(radius, location):
    
    st.session_state.location = location
    radius_meters = miles_to_meters(radius)
    
    geocode_result = gmaps.geocode(location)
    if not geocode_result:
        return []

    lat_lng = geocode_result[0]["geometry"]["location"]
    places_result = gmaps.places_nearby(
        lat_lng, radius=radius_meters, keyword="farmers market", type="point_of_interest"
    )

    markets = []
    for market in places_result["results"]:
        name = market["name"]
        address = market["vicinity"]
        location = market["geometry"]["location"]
        phone_number = None
        hours = None

        place_details = gmaps.place(market["place_id"])
        if "formatted_phone_number" in place_details["result"]:
            phone_number = place_details["result"]["formatted_phone_number"]
        if "opening_hours" in place_details["result"]:
            hours = place_details["result"]["opening_hours"]["weekday_text"]

        markets.append({
            "name": name,
            "address": address,
            "location": location,
            "phone_number": phone_number,
            "hours": hours
        })
      
    st.session_state.markets[st.session_state.location] = markets
    st.session_state.radius_dict[st.session_state.location] = radius


    return markets  # This line should be at this level of indentation


def display_farmers_map(radius, location):
    markets = get_farmers_markets(radius, location)

    if markets:
        center_location = [markets[0]["location"]["lat"], markets[0]["location"]["lng"]]
        map = folium.Map(location=center_location)

        # Create a list to store the coordinates of the markers
        coordinates = []

        for market in markets:
            
            lat, lng = market["location"]["lat"], market["location"]["lng"]
            folium.Marker(
                [lat, lng],
                popup=f"<strong>{market['name']}</strong><br>{market['address']}<br>{market['phone_number']}",
                tooltip=market['name'],
            ).add_to(map)
            coordinates.append([lat, lng])

        # Create a custom JavaScript function to fit the map view to the markers' bounds
        fit_bounds_script = f"""
        <script>
            setTimeout(function() {{
                map_{map._id}.fitBounds({coordinates});
            }}, 300);
        </script>
        """

        # Add a title to the map
        title_html = f"""
            <h3 style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 9999; background-color: white; padding: 5px; border-radius: 3px;">
                Farmer's Markets within {radius} miles of {st.session_state.location}
            </h3>
        """
        map.get_root().html.add_child(folium.Element(title_html))

        # Add the custom JavaScript function to the map
        map.get_root().html.add_child(folium.Element(fit_bounds_script))

    else:
        st.warning("No farmers markets found in the given location.")
    st.session_state.maps[st.session_state.location] = map

    return map

i=0

def get_new_farmers():
    st.markdown('---')
    with st.form(f"find_new_markets {i}, clear_on_submit=True"):
        location = st.session_state.location
       
        st.markdown(f'##### Select a search radius (in miles) to find farmers markets near {st.session_state.location}')
        radius = st.slider("Search radius (miles):", min_value=1, max_value=50, value=10, step=1)
        new_find_markets_button = st.form_submit_button(label='Find New Markets')
        
        # Displaying a list of the farmers markets info on one smaller column, and the map on the other
        if new_find_markets_button:
            with st.spinner('Finding farmers markets...'):
                st.session_state.location = location
                st.session_state.radius = radius
                markets = get_farmers_markets(radius, location)
                map = display_farmers_map(radius, location)
                st.markdown(f'#### Farmers Markets within {st.session_state.radius} miles of {st.session_state.location}')
                st.markdown(f'Details can be found by clicking on the markers on the map,\
                            and are listed below the map in an expandable table.')
                col1, col2 = st.columns([2,1], gap = 'large')

               
                folium_static(map)

              
                # Create a pandas dataframe from the name, address and phone_numbers of the
                # list of markets and display it beneath the map
                df = pd.DataFrame(markets)
                df = df[['name', 'address', 'phone_number', 'hours']]

                # Change first lett of the column names to uppercase and make the new "Name" column the index
                df.columns = df.columns.str.capitalize()
                df = df.set_index('Name')

                # Display the dataframe
                st.dataframe(df, use_container_width=True)
        
            # If the button is clicked, switch to the season page
    return_to_seasonal_button = st.button("Return to seasonal produce page", type = 'primary', use_container_width=True)
    if return_to_seasonal_button:
        st.session_state.seasonal_page = 'Find Produce'
        switch_page('Seasonal Produce')
    # If the button is clicked, switch to the home page
    return_home_farmers_button = st.button("Return to home page", type = 'primary', use_container_width=True)
    if return_home_farmers_button:
        switch_page('Home')






