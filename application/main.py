import streamlit as st
import folium
from streamlit_folium import st_folium
from datetime import datetime
import backend as backend
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
        gender = st.radio("Gender:", ["Male", "Female"], key="vic1")
        race = st.selectbox("Race:", ['WHITE', 'WHITE HISPANIC', 'BLACK', 'ASIAN / PACIFIC ISLANDER', 'BLACK HISPANIC',
                                      'AMERICAN INDIAN/ALASKAN NATIVE', 'OTHER'], key="vic2")
        age = st.slider("Age:", 0, 120, key="vic3")
        date = st.date_input("Date:", datetime.now())
        hour = st.slider("Hour:", min_value=0, max_value=24)
        place = st.radio("Place:", ("In park", "In public housing", "In station"))
        _, col, _ = st.sidebar.columns(3)
        with col:
            predict = st.button("Predict")

    return gender, race, age, predict, date, hour, place

st.title("New York Crime Prediction")
gender, race, age, predict, date, hour, place = get_user_information()
base_map = generate_base_map()
base_map.add_child(folium.LatLngPopup())

map = st_folium(base_map, height=350, width=700)
data = get_pos(map['last_clicked']['lat'],map['last_clicked']['lng'])

if data is not None:
    st.write(data)

lat=data[0]
long=data[1]

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