import streamlit as st
import folium
from streamlit_folium import st_folium,folium_static
from geopy.geocoders import Nominatim
from datetime import datetime
import backend as backend
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Proj, transform

def get_coordinates(destination):
    geolocator = Nominatim(user_agent="NYC_crimes")
    location = geolocator.geocode(destination)

    if location:
        return location.latitude, location.longitude
    else:
        return None

def get_pos(lat,lng):
    return lat,lng

def lon_lat_to_utm(lon, lat):
    # Define the projection for UTM (EPSG:2263)
    utm_proj = Proj(init="epsg:2263")

    # Transform latitude and longitude to UTM coordinates
    utm_x, utm_y = transform(Proj(init="epsg:4326"), utm_proj, lon, lat)

    return utm_x, utm_y

shapefile='application/geo_export_84578745-538d-401a-9cb5-34022c705879.shp'
borough_sh='application/borough/nybb.shp'

def get_precinct_and_borough(lat, lon):
    # Load the shapefiles
    precinct_gdf = gpd.read_file(shapefile)
    borough_gdf = gpd.read_file(borough_sh)

    # Create a Point object from the coordinates
    point = Point(lon, lat)
    point2=Point(lon_lat_to_utm(lon, lat))

    # Find the precinct and borough that contains the point
    precinct = None
    borough = None
    for _, row in precinct_gdf.iterrows():
        if row['geometry'].contains(point):
            precinct = row['precinct']
    for _, row in borough_gdf.iterrows():
        #print(row)
        if row['geometry'].contains(point2):
            borough = row['BoroName']
            break  # Exit the loop once a match is found
    return precinct, borough


def generate_base_map(default_location=[40.704467, -73.892246], default_zoom_start=11, min_zoom=11, max_zoom=15):
    base_map = folium.Map(location=default_location, control_scale=True, zoom_start=default_zoom_start,
                          min_zoom=min_zoom, max_zoom=max_zoom, max_bounds=True, min_lat=40.47739894,
                          min_lon=-74.25909008, max_lat=40.91617849, max_lon=-73.70018092)
    return base_map

def get_user_information(k1,k2,k3):
    with st.sidebar:
        st.header("Enter your information")
        gender = st.radio("Gender:", ["Male", "Female"], key=k1)
        race = st.selectbox("Race:", ['WHITE', 'WHITE HISPANIC', 'BLACK', 'ASIAN / PACIFIC ISLANDER', 'BLACK HISPANIC',
                                      'AMERICAN INDIAN/ALASKAN NATIVE', 'OTHER'], key=k2)
        age = st.slider("Age:", 0, 120, key="age")
        date = st.date_input("Date:", datetime.now(), key="date")
        hour = st.slider("Hour:", min_value=0, max_value=24, key="hour")
        place = st.radio("Place:", ("In park", "In public housing", "In station"), key=k3)

    return gender, race, age, date, hour, place


def get_user_input_method():
    return st.radio("Choose input method:", ["Text Input", "Map Click"])

st.title("New York Crime Prediction")
input_method = get_user_input_method()
gender, race, age, date, hour, place=get_user_information("gender","race","place")


if input_method == "Text Input":
    destination = st.text_input("Enter your destination:")
    if st.button("Get Coordinates"):
        coordinates = get_coordinates(destination)
        lat=coordinates[0]
        long=coordinates[1]
        precinct,borough=get_precinct_and_borough(lat, long)
        print(precinct,borough)
        if coordinates:
            st.success(f"Coordinates for {destination}: {coordinates}")
            st.success(f'precinct = {precinct},borough ={borough} ')
            # Create a map with the destination marker
            base_map = folium.Map(location=coordinates, zoom_start=15)
            folium.Marker(location=coordinates, popup=destination).add_to(base_map)
            # Display the map
            folium_static(base_map)
            _, col, _ = st.columns(3)
            with col:
                predict = st.button("Predict", key="predict")
            if predict:
                if lat=='' or long == '' or precinct==None :
                    st.error("Please make sure that you selected a location on the map")    
                    if st.button("Okay"):
                        pass
                else:
                    X = backend.create_df(date, hour, lat, long, place, age, race, gender, precinct, borough)
                    pred, crimes = backend.predict(X)
                    st.markdown(f"You are likely to be a victim of: **{pred}**")
                    st.markdown(f"#### Some of the crimes types are the following: ")
                    st.markdown(crimes)
        else:
            st.error("Unable to retrieve coordinates for the given destination.")
        

elif input_method == "Map Click":
    base_map = generate_base_map()
    base_map.add_child(folium.LatLngPopup())

    map = st_folium(base_map, height=350, width=700)
    data = get_pos(map['last_clicked']['lat'], map['last_clicked']['lng'])

    if data is not None:
        st.write(data)

    lat = data[0]
    long = data[1]
    precinct,borough=get_precinct_and_borough(lat, long)
    print(precinct,borough)
    st.success(f"Coordinates are {lat}: {long}")
    st.success(f'precinct = {precinct},borough ={borough} ')
    _, col, _ = st.columns(3)
    with col:
        predict = st.button("Predict", key="predict")
    if predict:
        if lat=='' or long == '' or precinct==None :
            st.error("Please make sure that you selected a location on the map")    
            if st.button("Okay"):
                pass
        else:
            X = backend.create_df(date, hour, lat, long, place, age, race, gender, precinct, borough)
            pred, crimes = backend.predict(X)
            st.markdown(f"You are likely to be a victim of a : **{pred}** crime")
            st.markdown(f"#### Some of the crimes types are the following: ")
            st.markdown(crimes)