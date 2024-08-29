import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from shapely.geometry import Point
import time
from src.forest_model import ForestModel
from shapely.geometry import Point, Polygon
from shapely.affinity import scale

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
            html.H2("Simulation Setup", style={'font-family': 'Georgia', 'margin-bottom': '20px'}),

            html.Label("Wind Speed", style={'font-family': 'Georgia'}),
            dcc.Input(id='wind-speed', type='number', placeholder="Enter wind speed",
                      style={'margin-bottom': '10px', 'width': '100%'}),

            html.Label("Wind Direction", style={'font-family': 'Georgia'}),
            dcc.Input(id='wind-direction', type='text', placeholder="Enter wind direction",
                      style={'margin-bottom': '10px', 'width': '100%'}),

            html.Label("Humidity", style={'font-family': 'Georgia'}),
            dcc.Input(id='humidity', type='number', placeholder="Enter humidity",
                      style={'margin-bottom': '10px', 'width': '100%'}),

            html.Label("Density", style={'font-family': 'Georgia'}),
            dcc.Input(id='density', type='number', placeholder="Enter density",
                      style={'margin-bottom': '10px', 'width': '100%'}),

            html.Label("Temperature", style={'font-family': 'Georgia'}),
            dcc.Input(id='temperature', type='number', placeholder="Enter temperature",
                      style={'margin-bottom': '20px', 'width': '100%'}),

            html.Button('Run Simulation', id='run-button', n_clicks=0,
                        style={'margin-top': '20px', 'font-family': 'Georgia'}),

        ], style={'width': '35%', 'padding': '20px', 'display': 'inline-block', 'vertical-align': 'top'}),

        # Right-hand side (65% width)
        html.Div([

            # Time slider and play button below the map
            html.Div([
                html.Button('Play', id='play-button', n_clicks=0,
                            style={'margin-right': '10px', 'font-family': 'Georgia'}),
                dcc.Slider(
                    id='time-slider',
                    min=data['step_count'].min(),
                    max=data['step_count'].max(),
                    value=data['step_count'].min(),
                    marks={str(step): str(step) for step in data['step_count'].unique()},
                    step=None,
                )
            ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center',
                      'margin-top': '20px', 'height': '20px'}),

            # First section on the right-hand side (60% height)
            html.Div([
                dcc.Graph(id='map', config={'scrollZoom': False}, style={'height': '65vh'}),
            ], style={'height': '60%'}),

            # Second section on the right-hand side (40% height)
            html.Div([
                dcc.Graph(id='timeseries', style={'height': '30vh'})
            ], style={'height': '35%', 'margin-top': '20px'})

        ], style={'width': '63%', 'display': 'inline-block', 'margin-left': '2%'})
    ], style={'display': 'flex', 'width': '100%'}),

    # Hidden store for intermediate results
    dcc.Store(id='simulation-data')

])


# Callback to update the map based on the time slider value
@app.callback(
    Output('map', 'figure'),
    Input('time-slider', 'value'),
)
def update_map(step):
    filtered_data = data[data['step_count'] == step]
    fig = px.scatter_mapbox(
        filtered_data, lat="lat", lon="lon", size="value", color="value",
        center={"lat": 42.81852, "lon": -1.64323},  # Centered on Pamplona
        zoom=13, height=600
    )
    fig.update_layout(mapbox_style="open-street-map")
    return fig


# Callback to animate the map based on the play button click
@app.callback(
    Output('time-slider', 'value'),
    Input('play-button', 'n_clicks'),
    State('time-slider', 'value')
)
def animate_map(n_clicks, current_value):
    if n_clicks > 0:
        for step in range(current_value, data['step_count'].max() + 1):
            time.sleep(1)  # Simulate time step (can be adjusted)
            return step  # Update the time slider value to animate the map
    return current_value


# Placeholder for the timeseries plot (could be filled with actual data)
@app.callback(
    Output('simulation-data', 'data'),
    Input('run-button', 'n_clicks')
)
def update_timeseries(n_clicks):
    if n_clicks > 0:

        # run simulation here:
        # create an initial Shapely area
        center_point = Point(-1.64323, 42.81852)

        # Define an initial square polygon around the center point
        initial_square = Polygon([
            (center_point.x - 0.01, center_point.y - 0.01),
            (center_point.x + 0.01, center_point.y - 0.01),
            (center_point.x + 0.01, center_point.y + 0.01),
            (center_point.x - 0.01, center_point.y + 0.01)
        ])

        # Scale the square polygon to cover approximately 2 square kilometers
        scaling_factor = (1 / initial_square.area) ** 0.5  # Scale to get 2 km^2
        scaled_square = scale(initial_square, xfact=scaling_factor, yfact=scaling_factor)
        forest_areas = [{"name": "Area1",
                         "area": scaled_square,
                         "vegetation": [{"tree": "pine", "tree_density_m": 0.1},
                                        {"tree": "oak", "tree_density_m": 0.1}]}]

        scaling_factor = (0.1 / initial_square.area) ** 0.5
        scaled_square = scale(initial_square, xfact=scaling_factor, yfact=scaling_factor)

        fire_area = [{"name": "Fire_Area1", "area": scaled_square}]
        forest_model = ForestModel(areas=forest_areas,
                                   wind_conditions={"speed": 100, "direction": 45},
                                   humidity_conditions={"rain": False, "wet": False, "humidity": 60})

        forest_model.initialise_fire(fire_areas=fire_area)
        results = forest_model.run_simulation(simulation_time=100)
        return results

    return {}


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)