import subprocess
import re
import sys

# Regular expressions to locate sections in the oplrun output
evac_start_pattern = re.compile(r"evac\.csv:")
vehicles_start_pattern = re.compile(r"vehicles\.csv:")

def parse_and_write_csv(output):
    evac_lines = []
    vehicles_lines = []

    # Split the output into lines
    lines = output.splitlines()

    # Flags to identify the current section
    in_evac_section = False
    in_vehicles_section = False

    for line in lines:
        if evac_start_pattern.search(line):
            in_evac_section = True
            in_vehicles_section = False
            continue
        elif vehicles_start_pattern.search(line):
            in_evac_section = False
            in_vehicles_section = True
            continue
        elif line.strip() == "<<< post process" or line.strip() == "<<< done":
            # Stop parsing when we reach these markers
            in_vehicles_section = False
            in_evac_section = False

        if in_evac_section:
            evac_lines.append(line.strip())
        elif in_vehicles_section:
            # Validate the line structure before adding
            if re.match(r"^\d+(,\d+)*$", line.strip()):
                vehicles_lines.append(line.strip())

    # Write evac.csv
    with open("evac.csv", "w") as evac_file:
        evac_file.write("\n".join(evac_lines))
    print("evac.csv written successfully.")

    # Write vehicles.csv
    with open("vehicles.csv", "w") as vehicles_file:
        vehicles_file.write("\n".join(vehicles_lines))
    print("vehicles.csv written successfully.")

def run_opl_and_generate_csv(opl_executable, mod_file, dat_file):
    try:
        # Construct the command
        command = [opl_executable, mod_file, dat_file]

        # Run the command and capture output
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, _ = process.communicate()  # Get full output

        # Parse the output and generate CSV files
        parse_and_write_csv(output)

    except Exception as e:
        print("Error running oplrun or processing output:", e)

if __name__ == "__main__":
    # Ensure the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python solve.py <mod_file> <dat_file>")
        sys.exit(1)

    # Extract file paths from arguments
    mod_file = sys.argv[1]
    dat_file = sys.argv[2]

    # Path to oplrun executable
    opl_executable = "/home/alierdem/cplex/opl/bin/x86-64_linux/oplrun"

    # Run the OPL model and generate CSV files
    run_opl_and_generate_csv(opl_executable, mod_file, dat_file)

