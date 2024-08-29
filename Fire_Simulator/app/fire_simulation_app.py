import streamlit as st
import pydeck as pdk
import time


class FireSimulationApp:

    def __init__(self, data, area):

        # Streamlit interface
        st.title("Shapely Points on Geomap (Blue Circles)")

        #geo_json = GeoJson(area.__geo_interface__, style_function=lambda x: {
        #    "color": "blue",
        #    "weight": 2,
        #    "fillOpacity": 0.1
        #}).add_to(m)

        # Get unique steps
        steps = data['step_count'].unique()

        # Placeholder for the map
        map_placeholder = st.empty()

        # Loop through each time step
        for step in steps:
            # Filter the data for the current step
            step_data = data[data['step_count'] == step]

            # Convert locations to latitude and longitude
            step_data['lat'] = step_data['location'].apply(lambda p: p.y)
            step_data['lon'] = step_data['location'].apply(lambda p: p.x)

            # Create a PyDeck scatter plot layer
            layer = pdk.Layer(
                "ScatterplotLayer",
                step_data,
                get_position='[lon, lat]',
                get_color='color',
                get_radius=200,
                pickable=True
            )

            # Set the initial view state of the map
            view_state = pdk.ViewState(
                latitude=step_data['lat'].mean(),
                longitude=step_data['lon'].mean(),
                zoom=13,
                pitch=0
            )

            # Add a delay to animate
            time.sleep(1)

        # Display the map in Streamlit