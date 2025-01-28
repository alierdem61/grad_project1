
# CSE495 Graduation Project

## Authors

**Ali Erdem Akyüz**

**Hüseyin Emre Tığcı**

## About the project

This project includes a CPLEX OPL implementation of the JESDRA model (in file `jesdra.mod`) from the article [A joint demand and supply management approach to large scale urban evacuation planning: Evacuate or shelter-in-place, staging and dynamic resource allocation](https://www.sciencedirect.com/science/article/abs/pii/S0377221723005921), and data files for the toy example in the article (`toy.dat`), a small area we chose in Dallas (`dallas.dat`) and a large area we chose in Chicago that roughly equals in size the Fort Worth road network in the article (`chicago.dat`).
It also includes code that uses the `oplrun` CLI for solving (`solve.py`), code that visualizes the outputs of two decision variables on a map (`visualize.py`), and a Python GUI application that combines these two (`gui.py`).

## Trailer

You can watch our trailer video [here](https://www.youtube.com/watch?v=lqILgtYLC5Q) to learn more about our project.

## Limitations

Dynamic resource allocation is an important aspect of the article. Unfortunately, our implementation of the JESDRA model is currently unable to make any resource allocation.
The Chicago data we generated is moderately accurate. However, the risk values are fully randomized. We calculated realistic values for the risk factors in the other data files, but we could not prepare the needed data for the calculation for the Chicago data due to time limitations. You can read more about our data preparation below.

## Data preparation

The toy example in the article had most of the data we needed. Even though the risk factors and resource travel times were not explicitly given, we could calculate them as the coordinates of the cells and the disaster can be roughly deduced. We decided to put these coordinates and other related info into a JSON file which we use for the risk calculation and also visualization. We calculated the risk values by taking the inverse of the square of the distance between each cell and the disaster, and normalized it between 0 and 1 (see `calculate_risk.py`). For resource travel times, we used the shortest path between each node using cell counts between nodes as the weight of the edge between them (see `calculate_tau.py`).
We couldn't prepare the JSON file for the Chicago data due to time constraints, hence the aforementioned randomized risk values. We did however manage to calculate the resource travel times.

## How to run

### Install dependencies

You need to install the following:
- CPLEX
- Python
- Python packages Dash, Dash Leaflet, Flask (For the visualization code)

### Running `solve.py`

You need to provide the path to your `oplrun` executable within the main function in `solve.py`. It should be in somewhere like `cplex/opl/bin/${your_os}/oplrun`. Then to use the command `python solve.py jesdra.mod toy.dat` to run the solver with the toy example data. You may also run it with different `.dat` files.
The program will produce 2 CSV files which contain the output of the decision variables, which are used by the visualization program.

### Running `visualize.py`

The visualization code needs information about the locations of each cell, the speed and direction of the disaster and more. The information should be provided to the visualization code via a JSON file. We have ready-to-use JSON files (`toy_info.json` and `dallas_info.json`) which have the necessary info for the toy example and the Dallas road network. We could not produce this JSON file for the Chicago area due to time constraints, which means the visualization cannot be done for the Chicago data.
Provided that you have already run the solver with the toy example data, use `python visualize.py toy_info.json` to use visualize the output for the toy example. This will start a Flask server, which you can view in your browser.
The legend at the bottom left of the page should be clear enough for you to understand what is being shown. The heatmap depicts the vehicle count in each cell at each timestep. You can also hover over each cell to see its type and the number of vehicles in that cell at that timestep.

### Running `gui.py`
The GUI will make the process of solving and visualizing much easier. It allows you to select the necessary files, and can the solver and visualizer sequentially with one click. Use `python gui.py` to run the program.
