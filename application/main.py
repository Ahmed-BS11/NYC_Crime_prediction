import streamlit as st
import folium
from streamlit_folium import st_folium,folium_static
from geopy.geocoders import Nominatim
from datetime import datetime
import backend as backend

def get_coordinates(destination):
    geolocator = Nominatim(user_agent="NYC_crimes")
    location = geolocator.geocode(destination)

    if location:
        return location.latitude, location.longitude
    else:
        return None

def get_pos(lat,lng):
    return lat,lng

def generate_base_map(default_location=[40.704467, -73.892246], default_zoom_start=11, min_zoom=11, max_zoom=15):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start,
                          min_zoom=min_zoom, max_zoom=max_zoom, max_bounds=True, min_lat=40.47739894,
                          min_lon=-74.25909008, max_lat=40.91617849, max_lon=-73.70018092)
    return base_map

def get_user_information():
    with st.sidebar:
        st.header("Enter your information")
        gender = st.radio("Gender:", ["Male", "Female"], key="gender")
        race = st.selectbox("Race:", ['WHITE', 'WHITE HISPANIC', 'BLACK', 'ASIAN / PACIFIC ISLANDER', 'BLACK HISPANIC',
                                      'AMERICAN INDIAN/ALASKAN NATIVE', 'OTHER'], key="race")
        age = st.slider("Age:", 0, 120, key="age")
        date = st.date_input("Date:", datetime.now(), key="date")
        hour = st.slider("Hour:", min_value=0, max_value=24, key="hour")
        place = st.radio("Place:", ("In park", "In public housing", "In station"), key="place")
        _, col, _ = st.sidebar.columns(3)
        with col:
            predict = st.button("Predict", key="predict")

    return gender, race, age, predict, date, hour, place


def get_user_input_method():
    return st.radio("Choose input method:", ["Text Input", "Map Click"])

st.title("New York Crime Prediction")
get_user_information()
input_method = get_user_input_method()

if input_method == "Text Input":
    destination = st.text_input("Enter your destination:")
    if st.button("Get Coordinates"):
        coordinates = get_coordinates(destination)
        if coordinates:
            st.success(f"Coordinates for {destination}: {coordinates}")
            # Create a map with the destination marker
            base_map = folium.Map(location=coordinates, zoom_start=15)
            folium.Marker(location=coordinates, popup=destination).add_to(base_map)
            # Display the map
            folium_static(base_map)
        else:
            st.error("Unable to retrieve coordinates for the given destination.")

elif input_method == "Map Click":
    gender, race, age, predict, date, hour, place = get_user_information()
    base_map = generate_base_map()
    base_map.add_child(folium.LatLngPopup())

    map = st_folium(base_map, height=350, width=700)
    data = get_pos(map['last_clicked']['lat'], map['last_clicked']['lng'])

    if data is not None:
        st.write(data)

    lat = data[0]
    long = data[1]

if predict:
    if lat=='' or long == '':
        st.error("Please make sure that you selected a location on the map")    
        if st.button("Okay"):
            pass
    else:
        X = backend.create_df(hour,date.month,date.day,lat,long,place,age,race,gender)
        pred, crimes = backend.predict(X)
        st.markdown(f"You are likely to be a victim of: **{pred}**")
        st.markdown(f"#### Some of the crimes types are the following: ")
        st.markdown(crimes)