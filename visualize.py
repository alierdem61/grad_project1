import argparse
import json
import math
import csv
from dash import Dash, html, dcc
import dash_leaflet as dl
from dash.dependencies import Input, Output
from threading import Timer
from flask import request


# Argument parsing
parser = argparse.ArgumentParser(description="Run visualization with specified JSON file.")
parser.add_argument("json_file", help="Path to the JSON file containing coordinates and settings.")
args = parser.parse_args()

# Load data
with open(args.json_file, 'r') as f:
    data = json.load(f)

cells = data['cells']
disaster = data['disaster']
settings = data['setting']

unit_length = settings['unit_length_in_meters']
time_step_length = settings['time_step_length_in_secs']

# Geographic center for cell 5
center_lat = settings['geo_center']['lat']
center_lon = settings['geo_center']['lon']

def convert_to_geographic(cartesian_coords, unit_length):
    x_meters = cartesian_coords[0] * unit_length
    y_meters = cartesian_coords[1] * unit_length
    earth_radius = 6378137.0

    # Latitude offset in degrees
    latitude = center_lat + (y_meters / earth_radius) * (180 / math.pi)
    # Longitude offset in degrees (adjusted for latitude)
    longitude = center_lon + (x_meters / (earth_radius * math.cos(math.radians(center_lat)))) * (180 / math.pi)

    return latitude, longitude


geo_cells = [{
    'cell_number': cell['cell_number'],
    'geo_coords': convert_to_geographic((cell['x_coord'], cell['y_coord']), unit_length),
    'type': cell['type']  # Use the new 'type' field
} for cell in cells]

disaster_geo_coords = convert_to_geographic((disaster['x_coord'], disaster['y_coord']), unit_length)

# Read vehicle counts
vehicle_counts = []
with open('vehicles.csv', 'r') as vehicles_file:
    reader = csv.reader(vehicles_file)
    for row in reader:
        vehicle_counts.append([int(value) for value in row])

evacuation_orders = {}
with open('evac.csv', 'r') as evac_file:
    reader = csv.reader(evac_file)
    for row in reader:
        cell_number = int(row[0])
        evacuation_orders[cell_number] = int(row[1])  # 1: evacuation order, 0: no order


# Helper: Determine color based on vehicle count
# Adjust get_color to consider evacuation status
def get_color(vehicle_count, max_count, evacuated):
    if not evacuated:
        return "rgb(0,0,0)"  # Black for no evacuation order
    if max_count == 0:
        return "rgb(0,0,255)"  # Default to blue if max count is zero
    normalized = vehicle_count / max_count
    r = int(255 * normalized)  # Red increases with count
    g = int(255 * (1 - normalized) * normalized * 4)  # Creates purple-orange transition
    b = int(255 * (1 - normalized))  # Blue decreases with count
    return f"rgb({r},{g},{b})"

# Dash app
app = Dash(__name__)

app.layout = html.Div([
    dcc.Interval(id="interval", interval=time_step_length * 1000, n_intervals=0),
    dl.Map([
    dl.TileLayer(),
    dl.LayerGroup(id="circles"),  # Placeholder for circles
    dl.LayerGroup(id="disaster")  # Placeholder for disaster
], center=[center_lat, center_lon], zoom=17, style={'height': '100vh'}),

html.Div(
    id="legend",
    style={
        "position": "absolute",
        "bottom": "10px",
        "left": "10px",
        "backgroundColor": "white",
        "padding": "10px",
        "borderRadius": "5px",
        "boxShadow": "0px 2px 5px rgba(0,0,0,0.2)",
        "zIndex": "1000"  # Ensures legend appears above the map
    },
    children=[
        html.Div([
            html.Div(
                style={
                    "display": "inline-block",
                    "width": "20px",
                    "height": "20px",
                    "border": "2px solid black",
                    "borderRadius": "50%",
                    "marginRight": "10px"
                }
            ),
            html.Span("Source/Shelter")
        ], style={"marginBottom": "10px"}),
        html.Div([
            html.Div(
                style={
                    "display": "inline-block",
                    "width": "20px",
                    "height": "20px",
                    "border": "2px solid black",
                    "marginRight": "10px"
                }
            ),
            html.Span("Road Cell")
        ]),
        html.Div([
            html.Div(
                style={
                    "display": "inline-block",
                    "width": "20px",
                    "height": "20px",
                    "border": "2px solid red",
                    "borderRadius": "50%",
                    "position": "relative",
                    "marginRight": "10px"
                }
            ),
            html.Span("Disaster")
        ]),
        html.Div([
            html.Div(
                style={
                    "display": "inline-block",
                    "width": "20px",
                    "height": "20px",
                    "backgroundColor": "black",
                    "borderRadius": "50%",
                    "marginRight": "10px"
                }
            ),
            html.Span("Shelter-in-place")
        ], style={"marginBottom": "10px"}),
        html.Div([
            html.Div(
                style={
                    "display": "inline-block",
                    "width": "100px",
                    "height": "20px",
                    "background": "linear-gradient(to right, rgb(0,0,255), rgb(255,0,0))",
                    "marginRight": "10px"
                }
            ),
            html.Span("More vehicles = warmer color")
        ]),
    ]
)

])

@app.server.route('/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the server cleanly."""
    shutdown_func = request.environ.get('werkzeug.server.shutdown')
    if shutdown_func:
        shutdown_func()
    return 'Server shutting down...', 200

@app.callback(
    [Output("circles", "children"), Output("disaster", "children")],
    [Input("interval", "n_intervals")]
)
def update_map(n):
    try:
        if n >= len(vehicle_counts[0]):
            print("No updates: All time steps processed.")
            return [], []  # No updates after max time steps
        
        # Debug: Check callback trigger
        print(f"Callback triggered for time step {n}")

        # Calculate max vehicle count for this time step
        max_count = max(vehicle_counts[i][n] for i in range(len(vehicle_counts)))
        
        # Debug: Print max count and vehicle counts
        print(f"Time Step {n}: Max Vehicle Count = {max_count}")
        print(f"Vehicle Counts: {[vehicle_counts[i][n] for i in range(len(vehicle_counts))]}")

        # Create Circles and Rectangles for cells
        cell_size = 0.0002  # Smaller size for rectangles
        elements = []
        for i, cell in enumerate(geo_cells):
            # Check evacuation status; default is not restricted
            evacuation_status = evacuation_orders.get(cell["cell_number"], None)
            if evacuation_status == 0:  # Explicit evacuation restriction
                color = "rgb(0,0,0)"  # Black for restricted cells
            else:
                color = get_color(vehicle_counts[i][n], max_count, True)  # Heatmap for all other cases
            
            if cell["type"] == "road":
                elements.append(
                    dl.Rectangle(
                        id=f"road-{cell['cell_number']}-{n}",  # Unique ID for road rectangles
                        bounds=[
                            [cell['geo_coords'][0] - cell_size, cell['geo_coords'][1] - cell_size],
                            [cell['geo_coords'][0] + cell_size, cell['geo_coords'][1] + cell_size]
                        ],
                        color=color,
                        fill=True,
                        fillOpacity=0.7,
                        children=dl.Tooltip(f"Road Cell {cell['cell_number']} Vehicles: {vehicle_counts[i][n]}")
                    )
                )
            else:
                elements.append(
                    dl.CircleMarker(
                        id=f"circle-{cell['cell_number']}-{n}",  # Unique ID for non-road cells
                        center=cell['geo_coords'],
                        radius=cell_size * 1 * 10**5,
                        color=color,
                        fill=True,
                        fillOpacity=0.7,
                        children=dl.Tooltip(f"{cell['type'].capitalize()} Cell {cell['cell_number']} Vehicles: {vehicle_counts[i][n]}")
                    )
                )
        
        # Disaster position (eastward movement along +x direction)
        distance_traveled = disaster['velocity_in_kmh'] * 1000 / 3600 * n * time_step_length
        disaster_lon = disaster_geo_coords[1] + (distance_traveled / (6378137.0 * math.cos(math.radians(disaster_geo_coords[0])))) * (180 / math.pi)
        print(f"Disaster Longitude: {disaster_lon}, Radius in Meters: {disaster['radius_in_meters']}")  # Debug
        
        disaster_circle = dl.Circle(
            center=(disaster_geo_coords[0], disaster_lon),
            radius=disaster['radius_in_meters'],  # Radius in meters
            color='red', fill=False, weight=2
        )
        
        return elements, [disaster_circle]

    except Exception as e:
        print("Error in callback:", e)
        return [], []

if __name__ == "__main__":
    
    app.run_server(debug=False)



