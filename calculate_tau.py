import math
import numpy as np
import json
import networkx as nx

# Load data from JSON file
with open('real_coords.json', 'r') as f:
    data = json.load(f)

# Extract necessary data
cells = data['cells']
disaster = data['disaster']
settings = data['setting']

# Settings
unit_length = settings['unit_length_in_meters']
time_step_length = settings['time_step_length_in_secs']
n_time_steps = settings['n_time_steps']
disaster_speed = disaster['velocity_in_kmh'] * 1000 / 3600  # convert to m/s
direction = disaster['direction']
disaster_radius = disaster['radius_in_meters']

# Initial disaster position
disaster_x = disaster['x_coord'] * unit_length
disaster_y = disaster['y_coord'] * unit_length

# Example node connectivity for tau computation
connections = [
    (1, 2, 'arterial'),
    (2, 1, 'arterial'),

    (2, 3, 'arterial'),
    (3, 2, 'arterial'),

    (3, 6, 'arterial'),
    (6, 3, 'arterial'),

    (6, 9, 'arterial'),
    (9, 6, 'arterial'),

    (4, 1, 'arterial'),
    (1, 4, 'arterial'),

    (7, 4, 'arterial'),
    (4, 7, 'arterial'),

    (5, 2, 'arterial'),
    (2, 5, 'arterial'),

    (5, 4, 'arterial'),
    (4, 5, 'arterial'),

    (6, 5, 'arterial'),
    (5, 6, 'arterial'),

    (8, 5, 'arterial'),
    (5, 8, 'arterial'),

]

# Define speeds (in meters per second)
speed_lookup = {
    'local': 36 / 3.6,  # Local streets: 36 km/h
    'arterial': 72 / 3.6  # Arterial roads: 72 km/h
}

# Define cell lengths
cell_length_lookup = {
    'local': 20,  # Local streets: 20 meters
    'arterial': 40  # Arterial roads: 40 meters
}

# Create a directed graph for shortest path computation
G = nx.DiGraph()
for start, end, road_type in connections:
    speed = speed_lookup[road_type]
    cell_length = cell_length_lookup[road_type]
    travel_time = math.ceil((cell_length / speed) / time_step_length)  # Calculate travel time in time steps
    G.add_edge(start, end, weight=travel_time)

# Nodes in Vp (exclude nodes 1 and 3)
Vp = [2, 4, 5, 6, 7, 8, 9]
resources = [1, 2]  # Example resources

# Initialize tau and tau_max arrays
num_nodes = len(Vp)
num_resources = len(resources)
tau = np.zeros((num_resources, num_nodes, num_nodes), dtype=int)
tau_max = np.zeros((num_resources, num_nodes), dtype=int)

# Add high-cost edges for disconnected components
for n1 in Vp:
    for n2 in Vp:
        if n1 != n2 and not nx.has_path(G, n1, n2):
            G.add_edge(n1, n2, weight=1000)  # High cost for disconnected nodes

# Compute shortest path travel times (tau) using Dijkstra's algorithm
for p_idx, p in enumerate(resources):
    for i, n1 in enumerate(Vp):
        lengths = nx.single_source_dijkstra_path_length(G, n1)
        for j, n2 in enumerate(Vp):
            tau[p_idx][i][j] = int(lengths.get(n2, np.inf))  # Use infinity if no path exists

# Compute tau_max values
for p_idx, p in enumerate(resources):
    for i, n in enumerate(Vp):
        tau_max[p_idx][i] = int(np.max(tau[p_idx][i, :]))

# Replace infinities with -1 for readability
tau = np.where(tau == np.inf, -1, tau).astype(int)

# Print tau and tau_max
print("3D array tau[p][n1][n2]:", tau.tolist())
print("2D array tau_max[p][n]:", tau_max.tolist())

