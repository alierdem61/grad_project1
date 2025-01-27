import numpy as np

def floyd_warshall(nodes, edges):
    # Initialize the distance matrix with infinity
    n = len(nodes)
    distance = np.full((n, n), float('inf'))

    # Map nodes to indices for easier matrix manipulation
    node_to_index = {node: i for i, node in enumerate(nodes)}

    # Distance to self is zero
    for i in range(n):
        distance[i][i] = 0

    # Set distances for the given edges
    for edge in edges:
        node1, node2, weight = edge
        i, j = node_to_index[node1], node_to_index[node2]
        distance[i][j] = weight
        distance[j][i] = weight  # Since the graph is undirected

    # Floyd-Warshall algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                distance[i][j] = min(distance[i][j], distance[i][k] + distance[k][j])

    return distance

# Read graph data from a file
def read_graph_from_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # First line contains nodes, comma-separated
    nodes = lines[0].strip().split(',')

    # Remaining lines contain edges in the format 'node1 node2 weight'
    edges = []
    for line in lines[1:]:
        parts = line.strip().split()
        edges.append((parts[0], parts[1], float(parts[2])))

    return nodes, edges

# Main function
if __name__ == "__main__":
    filename = input("Enter the filename containing the graph data: ")
    nodes, edges = read_graph_from_file(filename)

    # Calculate shortest paths
    distance_matrix = floyd_warshall(nodes, edges)

    # Output the result as a two-dimensional array
    print("\nShortest path matrix:")
    output_filename = "shortest_path_output.txt"
    largest_values_filename = "largest_values_output.txt"
    with open(output_filename, "w") as outfile:
        formatted_matrix = []
        largest_values = []
        for row in distance_matrix:
            formatted_row = [int(round(x)) if x < float('inf') else 'inf' for x in row]
            formatted_matrix.append(formatted_row)
            largest_values.append(max([x for x in formatted_row if x != 'inf']))
        
        # Print and write the matrix as a valid 2D array
        print(formatted_matrix)
        outfile.write(str(formatted_matrix))

    # Write the largest values to a separate file
    with open(largest_values_filename, "w") as outfile:
        print("\nLargest values in each row:")
        print(largest_values)
        outfile.write(str(largest_values))

    print(f"The shortest path matrix has been saved to {output_filename}")
    print(f"The largest values array has been saved to {largest_values_filename}")

