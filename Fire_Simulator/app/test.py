import dash
from dash import dcc, html, Output, Input, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample DataFrame with initial points
data = pd.DataFrame({
    'lon': [-1.64323, -1.64423, -1.64523],
    'lat': [42.81852, 42.81952, 42.82052]
})

# Initial figure using px.scatter_mapbox
fig = px.scatter_mapbox(
    data,
    lon='lon',
    lat='lat',
    color_discrete_sequence=["red"],
    size_max=15,
    zoom=10,
    center={"lat": 42.81852, "lon": -1.64323},
    mapbox_style="open-street-map"
)

fig.update_layout(
    title='Interactive Mapbox Plot',
    margin=dict(r=0, l=0, b=0, t=0),
)

app.layout = html.Div([
    dcc.Graph(id='map', figure=fig),
    dcc.Store(id='click-data', data=None),
    html.Div(id='dummy-output'),  # Dummy div to trigger client-side callback
    dcc.Location(id='url', refresh=False),  # To ensure app does not reload
    html.Script("""
        document.getElementById('map').on('plotly_click', function(data) {
            if (data.points.length > 0) {
                var lat = data.points[0].lat;
                var lon = data.points[0].lon;

                // Update hidden div with the clicked lat and lon
                window.dash_clientside.callback({
                    id: 'click-data',
                    property: 'data'
                }, {lat: lat, lon: lon});
            }
        });

        // Capture clicks on empty space in the map
        document.getElementById('map').on('plotly_doubleclick', function(event) {
            var mapDiv = document.getElementById('map');
            var mapInstance = mapDiv._fullLayout.mapbox._subplot._scene;

            var bbox = mapDiv.getBoundingClientRect();
            var x = event.clientX - bbox.left;
            var y = event.clientY - bbox.top;

            var coords = mapInstance.unproject([x, y]);

            // Update hidden div with the clicked lat and lon
            window.dash_clientside.callback({
                id: 'click-data',
                property: 'data'
            }, {lat: coords.lat, lon: coords.lon});
        });
    """)
])

# Callback to update the map based on click data
@app.callback(
    Output('map', 'figure'),
    Input('click-data', 'data'),
    State('map', 'figure')
)
def update_map(click_data, figure):

    print(click_data)
    if click_data:
        lat = click_data['lat']
        lon = click_data['lon']

        new_lon = figure['data'][0]['lon'] + [lon]
        new_lat = figure['data'][0]['lat'] + [lat]

        fig = go.Figure(
            data=[
                go.Scattermapbox(
                    mode='lines+markers',
                    lon=new_lon,
                    lat=new_lat,
                    marker=dict(size=8, color='red'),
                    line=dict(width=2, color='blue'),
                    name='Updated Polygon Edges and Vertices'
                )
            ],
            layout=go.Layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=42.81852, lon=-1.64323),
                    zoom=10
                ),
                margin=dict(r=0, l=0, b=0, t=0),
                title='Interactive Mapbox Plot'
            )
        )
        return fig
    return figure

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)