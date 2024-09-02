import dash
import json
import math
import shapely
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from src.forest_model import ForestModel
from shapely.geometry import Point, Polygon
from shapely.affinity import scale
import re


custom_color_scale = [[0.0, "green"], [0.1, "yellow"], [0.3, "orange"], [0.4, "red"], [1.0, "black"]]

# Sample DataFrame with Shapely Points
data = pd.DataFrame({
    'location': [Point(-1.64323, 42.81852), Point(-1.64423, 42.81952), Point(-1.64523, 42.82052)],
    'value': [10, 20, 30],
    'step_count': [1, 2, 3]
})

# Convert Shapely Points to separate lat/lon columns
data['lon'] = data['location'].apply(lambda p: p.x)
data['lat'] = data['location'].apply(lambda p: p.y)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.Div([
        # Left-hand side (35% width)
        html.Div([

            # Metrics
            html.Div([
                html.H3("Simulation Setup", style={'font-family': 'Georgia', 'margin-bottom': '12px'}),
                html.Div([
                    # Row 1
                    html.Div([
                        html.Div([
                            html.H6("Wind Speed (m/s)", style={'text-align': 'left', 'margin-top': '5px',
                                                               'margin-bottom': '5px'}),
                            dcc.Input("80", id="wind-speed", style={'font-size': '12px', 'text-align': 'left'})
                        ], style={'width': '50%',  "height": "20px", 'display': 'inline-block'}),
                        html.Div([
                            html.H6("Wind Direction (º)", style={'text-align': 'left', 'margin-top': '5px',
                                                                 'margin-bottom': '5px'}),
                            dcc.Input("45", id="wind-direction", style={'font-size': '12px', 'text-align': 'left'})
                        ], style={'width': '50%',  "height": "20px", 'display': 'inline-block'})
                    ], style={'width': '100%'}),
                    # Row 2
                    html.Div([

                        html.Div([
                            html.H6("Humidity (%)", style={'text-align': 'left', 'margin-top': '5px',
                                                           'margin-bottom': '5px'}),
                            dcc.Input("60", id="humidity", style={'font-size': '12px',
                                                                  'text-align': 'left',
                                                                  'margin-top': '10px'})
                        ], style={'width': '50%', 'display': 'inline-block'}),

                        html.Div([
                            html.H6("Temperature (C)", style={'text-align': 'left', 'margin-top': '5px',
                                                              'margin-bottom': '5px'}),
                            dcc.Input("24", id="temperature", style={'font-size': '12px',
                                                                     'text-align': 'left',
                                                                     'margin-top': '10px'})
                        ], style={'width': '50%', 'display': 'inline-block'})

                    ], style={'width': '100%'})

                ], style={'display': 'flex', 'flex-wrap': 'wrap'}),
            ], style={'display': 'inline-block', 'vertical-align': 'top'}),

            # Tables
            html.Div([

                html.H6("Define forest areas", style={'font-family': 'Georgia', 'margin-bottom': '12px'}),

                html.Button('Add Area', id='area-button', n_clicks=0,
                            style={'margin-top': '12px', 'font-family': 'Georgia'}),

                dcc.Graph(id="area-table", figure=go.Figure(data=[go.Table(
                    header=dict(values=["Area Name", "Properties"], fill_color='paleturquoise', align='left'),
                    cells=dict(values=[], fill_color='lavender', align='left'))
                ]).update_layout(margin=dict(l=0, r=0, t=5, b=0)),
                          style={"width": "100%", 'padding': '0px', "align": "left", "height": "100px"}),

                html.H6("Define fire start areas", style={'font-family': 'Georgia', 'margin-bottom': '12px'}),

                html.Button('Add fire', id='fire-button', n_clicks=0,
                            style={'margin-top': '12px', 'font-family': 'Georgia'}),

                dcc.Graph(id="fire-table", figure=go.Figure(data=[go.Table(
                    header=dict(values=["Area Name", "Properties"], fill_color='paleturquoise', align='left'),
                    cells=dict(values=[], fill_color='lavender', align='left'))
                ]).update_layout(margin=dict(l=0, r=0, t=5, b=0)),
                          style={"width": "100%", 'padding': '0px', "align": "left", "height": "100px"}),

                html.Button('Run Simulation', id='run-button', n_clicks=0,
                            style={"width": "100%", 'margin-top': '12px', 'font-family': 'Georgia', "align": "left"})
            ], style={'display': 'inline-block', 'vertical-align': 'top', "width": "100%"})

        ], style={'width': '40%', 'display': 'inline-block', 'vertical-align': 'top'}),

        # Right-hand side (65% width)
        html.Div([

            html.H3("Results", style={'font-family': 'Georgia', 'margin-bottom': '12px'}),

            # Time slider and play button below the map
            html.Div([
                html.Button('Play', id='play-button', n_clicks=0,
                            style={'margin-right': '10px', 'font-family': 'Georgia'}),

                html.Div([
                    dcc.Slider(
                        id='time-slider',
                        min=0,
                        max=10,
                        value=0,
                        marks={str(step): str(step) for step in range(0, 11)},
                        step=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        updatemode='drag',
                        included=True
                    )], style={"width": "100%"}),
                dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0, disabled=True)],
                style={'display': 'flex', 'align-items': 'center', 'justify-content': 'space-between', 'margin-top': '12px'}),

            # First section on the right-hand side (60% height)
            html.Div([
                dcc.Graph(id='map',
                          figure=px.scatter_mapbox(
                              [],
                              zoom=6,
                              center={"lat": 42.81852, "lon": -1.64323},
                              mapbox_style="open-street-map").update_layout(margin=dict(l=0, r=0, t=5, b=0)))
            ], style={'height': '60%', "width": "100%"}),

            # Second section on the right-hand side (40% height)
            html.Div([
                dcc.Graph(id='timeseries', style={'height': '30vh'})
            ], style={'height': '35%', 'margin-top': '12px'})

        ],
            style={'width': '100%', 'display': 'inline-block', 'margin-left': '2%'})],
        style={'display': 'flex', 'width': '100%'}),

    # Hidden store for intermediate results
    dcc.Store(id='simulation-data'),
    dcc.Store(id='area-data', data={}),
    dcc.Store(id='fire-data', data={}),
    dcc.Store(id='clicked-data', data=[]),
])


# Play: Trigger loop
@app.callback(
    Output('interval-component', 'disabled'),
    Input('play-button', 'n_clicks'),
    State('interval-component', 'disabled'))
def toggle_interval(n_clicks, disabled):
    if n_clicks > 0:
        return not disabled
    return disabled


@app.callback(
    Output('time-slider', 'value'),
    Output('map', 'figure', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    State('map', 'figure'),
    State('time-slider', 'value'),
    State('simulation-data', 'data'), prevent_initial_call=True)
def animate_map(loop_step, fig, current_value, sim_data):

    if not sim_data:
        return current_value, fig

    sim_data = pd.DataFrame(sim_data)
    filtered_data = sim_data[sim_data['step_count'] == current_value]
    fig = go.Figure(fig)
    fig.update_traces(marker={"size": 10, "opacity": 0.6, "color": filtered_data["color"]})

    # Update value
    current_value += 1
    return current_value, fig


# Add Area
@app.callback(
    Output('map', 'figure', allow_duplicate=True),
    Output('area-table', 'figure', allow_duplicate=True),
    Output('area-button', 'children'),
    Output('area-data', 'data'),
    [Input('area-button', 'n_clicks'),
     State('map', 'relayoutData'),
     State('area-button', 'children'),
     State('map', 'figure'),
     State('area-data', 'data'),
     State('area-table', 'figure')],
    prevent_initial_call=True)
def add_area(n_clicks, relayout_data, text, fig, area_data, table):
    if n_clicks > 0:

        if text == "Add Area":
            fig = go.Figure(fig)
            fig.update_layout(dragmode="drawclosedpath")

            return fig, table, "Confirm Area", area_data

        elif text == "Confirm Area":

            # save surface data
            if "shapes" in relayout_data:

                fig = go.Figure(fig)
                table = go.Figure(table)
                table_data = [[], []]
                for ii, shape in enumerate(relayout_data["shapes"]):

                    # Extract coordinates from the path using regex
                    bounds = get_bounds(center_lat=fig.layout["mapbox"]["center"]["lat"],
                                        center_lon=fig.layout["mapbox"]["center"]["lon"],
                                        zoom_level=fig.layout["mapbox"]["zoom"], tile_size=256)

                    coords = re.findall(r"[MLHVCSQTAZ,]*\s*([\d.-]+),([\d.-]+)", shape["path"])
                    lons, lats = zip(*[(float(lon), float(lat)) for lon, lat in coords])
                    lons = [lo * (bounds["max_lon"] - bounds["min_lon"]) + bounds["min_lon"] for lo in lons]
                    lats = [la * (bounds["max_lat"] - bounds["min_lat"]) + bounds["min_lat"] for la in lats]

                    coordinates = list(zip(lons, lats))

                    # Step 1: Check if the polygon is closed
                    if coordinates[0] != coordinates[-1]:
                        # Step 2: Close the polygon by adding the first coordinate to the end
                        coordinates.append(coordinates[0])

                    area_data.update({f"Area_{ii + 1}": coordinates})
                    print(coordinates)

                    # Add new trace for the shape
                    fig.add_trace(go.Scattermapbox(
                        mode='lines',
                        lon=[p[0] for p in coordinates],
                        lat=[p[1] for p in coordinates],
                        line=dict(width=2, color='blue')))

                    # Update table
                    table_data[0].append(f"Area_{ii + 1}")
                    table_data[1].append("")

                table.update_traces(cells=dict(values=table_data))
                fig['layout']['shapes'] = []
                fig.update_layout(dragmode=False)

                return fig, table, "Add Area", area_data

    return fig, table, "Add Area", area_data


@app.callback(
    Output('map', 'figure', allow_duplicate=True),
    Output('fire-table', 'figure', allow_duplicate=True),
    Output('fire-button', 'children'),
    Output('fire-data', 'data'),
    [Input('fire-button', 'n_clicks'),
     State('map', 'relayoutData'),
     State('fire-button', 'children'),
     State('map', 'figure'),
     State('fire-data', 'data'),
     State('fire-table', 'figure')],
    prevent_initial_call=True)
def add_area(n_clicks, relayout_data, text, fig, fire_data, table):
    if n_clicks > 0:

        if text == "Add fire":
            fig = go.Figure(fig)
            fig.update_layout(dragmode="drawclosedpath")

            return fig, table, "Confirm fire", fire_data

        elif text == "Confirm fire":

            # save surface data
            if "shapes" in relayout_data:

                fig = go.Figure(fig)
                table = go.Figure(table)
                table_data = [[], []]
                for ii, shape in enumerate(relayout_data["shapes"]):

                    # Extract coordinates from the path using regex
                    bounds = get_bounds(center_lat=fig.layout["mapbox"]["center"]["lat"],
                                        center_lon=fig.layout["mapbox"]["center"]["lon"],
                                        zoom_level=fig.layout["mapbox"]["zoom"], tile_size=256)

                    coords = re.findall(r"[MLHVCSQTAZ,]*\s*([\d.-]+),([\d.-]+)", shape["path"])
                    lons, lats = zip(*[(float(lon), float(lat)) for lon, lat in coords])
                    lons = [lo * (bounds["max_lon"] - bounds["min_lon"]) + bounds["min_lon"] for lo in lons]
                    lats = [la * (bounds["max_lat"] - bounds["min_lat"]) + bounds["min_lat"] for la in lats]

                    coordinates = list(zip(lons, lats))

                    # Step 1: Check if the polygon is closed
                    if coordinates[0] != coordinates[-1]:
                        # Step 2: Close the polygon by adding the first coordinate to the end
                        coordinates.append(coordinates[0])

                    fire_data.update({f"Fire_{ii + 1}": coordinates})

                    # Add new trace for the shape
                    fig.add_trace(go.Scattermapbox(
                        mode='lines',
                        lon=lons,
                        lat=lats,
                        line=dict(width=2, color='red')))

                    # Update table
                    table_data[0].append(f"Area_{ii + 1}")
                    table_data[1].append("")

                table.update_traces(cells=dict(values=table_data))
                fig['layout']['shapes'] = []
                fig.update_layout(dragmode=False)

                return fig, table, "Add fire", fire_data

    return fig, table, "Add fire", fire_data


# Run simulation
@app.callback(
    Output('simulation-data', 'data'),
    Output('map', 'figure'),
    Input('run-button', 'n_clicks'),
    State('temperature', 'value'),
    State('humidity', 'value'),
    State('wind-speed', 'value'),
    State('wind-direction', 'value'),
    State('area-data', 'data'),
    State('fire-data', 'data'),
    State('map', 'figure'))
def run_simulation(n_clicks, temperature, humidity, wind_speed, wind_direction, area_data, fire_data, fig):
    if n_clicks > 0:

        # run simulation here:

        # Create area:
        forest_areas = []
        for name, this_area_data in area_data.items():
            poly = shapely.Polygon(this_area_data)
            print(poly.area)
            this_area = {"name": name,
                         "area": poly,
                         "vegetation": [{"tree": "pine", "tree_density_m": 0.1}]}
            forest_areas.append(this_area)

        fire_areas = []
        for name, this_fire_data in fire_data.items():
            poly = shapely.Polygon(this_fire_data)
            this_area = {"name": name,
                         "area": poly}
            fire_areas.append(this_area)

        forest_model = ForestModel(areas=forest_areas,
                                   wind_conditions={"speed": float(wind_speed), "direction": float(wind_direction)},
                                   humidity_conditions={"rain": False, "wet": False, "humidity": float(humidity)})

        forest_model.initialise_fire(fire_areas=fire_areas)
        print(len(forest_model.tree_agents))
        results = forest_model.run_simulation(simulation_time=10)
        results["x"] = results["location"].apply(lambda x: x.x)
        results["y"] = results["location"].apply(lambda x: x.y)

        results_plot = results.loc[results["step_count"] == 0, :]

        fig = go.Figure(fig)
        fig.add_trace(go.Scattermapbox(
            mode='markers',
            lon=results_plot['x'],
            lat=results_plot['y'],
            marker=dict(size=20, opacity=0.6, color=results_plot['color']),
            name='Fire Spread'
        ))

        results = results.loc[:, ["x", "y", "burning_value", "color", "step_count"]].to_dict()
        return results, fig

    return {}, fig


def get_bounds(center_lat, center_lon, zoom_level, tile_size=256):
    """
    Calculate the bounding box for a given zoom level and center coordinates.

    :param center_lat: Latitude of the center point
    :param center_lon: Longitude of the center point
    :param zoom_level: Zoom level of the map
    :param tile_size: Size of a tile in pixels (default 256)
    :return: Dictionary with min_lat, max_lat, min_lon, max_lon
    """
    # Number of tiles per row or column at the given zoom level
    n_tiles = 2 ** zoom_level

    # Size of the map in pixels at this zoom level
    map_size = tile_size * n_tiles

    # Calculate the size of one pixel in degrees
    pixel_size_degrees_lon = 360.0 / map_size
    pixel_size_degrees_lat = 180.0 / map_size

    # Calculate the size of the visible area in degrees
    delta_degrees_lon = pixel_size_degrees_lon * tile_size
    delta_degrees_lat = pixel_size_degrees_lat * tile_size

    # Calculate bounds
    min_lon = center_lon - delta_degrees_lon / 2.0
    max_lon = center_lon + delta_degrees_lon / 2.0
    min_lat = center_lat - delta_degrees_lat / 2.0
    max_lat = center_lat + delta_degrees_lat / 2.0

    return {
        'min_lat': min_lat,
        'max_lat': max_lat,
        'min_lon': min_lon,
        'max_lon': max_lon
    }


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
