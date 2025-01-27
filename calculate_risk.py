import math
import numpy as np
import json

# Enter the path of the JSON file here
json_path = 'toy_info.json'

# Load data from JSON file
with open(json_path, 'r') as f:
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

def calculate_risk(distance, radius):
    if distance > radius:
        return 0  # No risk outside the radius
    return 1 - (distance / radius) ** 2  # Scale risk between 0 and 1

# Prepare the output array
n_cells = len(cells)
risk_matrix = np.zeros((n_cells, n_time_steps))

# Calculate risk values for each time step
for t in range(n_time_steps):
    for i, cell in enumerate(cells):
        cell_x = cell['x_coord'] * unit_length
        cell_y = cell['y_coord'] * unit_length

        if cell['type'] == 'shelter':
            risk_matrix[i][t] = 0  # Shelters always have risk 0
        else:
            # Calculate Euclidean distance
            distance = math.sqrt((cell_x - disaster_x) ** 2 + (cell_y - disaster_y) ** 2)
            risk_matrix[i][t] = calculate_risk(distance, disaster_radius)

    # Update disaster position
    if direction == '+x':
        disaster_x += disaster_speed * time_step_length
    elif direction == '-x':
        disaster_x -= disaster_speed * time_step_length
    elif direction == '+y':
        disaster_y += disaster_speed * time_step_length
    elif direction == '-y':
        disaster_y -= disaster_speed * time_step_length

# Output the risk matrix
print("Risk matrix (c[i][t]):")
print(risk_matrix)

# Optionally save to a file in array format
output_file = 'risk_matrix.txt'
with open(output_file, 'w') as f:
    f.write('[')
    for i, row in enumerate(risk_matrix):
        f.write('[' + ', '.join(f'{val:.4f}' for val in row) + ']')
        if i < len(risk_matrix) - 1:
            f.write(',\n')
    f.write(']')

print(f"Risk matrix saved to {output_file}")

