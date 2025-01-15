import subprocess
import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import webbrowser
import requests

class FileSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Solve and Visualize")
        self.server_process = None  # Track the server process

        # Labels to display chosen file paths
        self.dat_label = tk.Label(root, text="No .dat file selected", fg="gray")
        self.dat_label.pack(pady=5)

        self.mod_label = tk.Label(root, text="No .mod file selected", fg="gray")
        self.mod_label.pack(pady=5)

        self.json_label = tk.Label(root, text="No .json file selected", fg="gray")
        self.json_label.pack(pady=5)

        # Buttons to select files
        self.dat_button = tk.Button(root, text="Choose .dat File", command=self.select_dat_file)
        self.dat_button.pack(pady=5)

        self.mod_button = tk.Button(root, text="Choose .mod File", command=self.select_mod_file)
        self.mod_button.pack(pady=5)

        self.json_button = tk.Button(root, text="Choose .json File", command=self.select_json_file)
        self.json_button.pack(pady=5)

        # Buttons for solving and visualization
        self.solve_button = tk.Button(root, text="Solve", command=self.run_solve)
        self.solve_button.pack(pady=5)

        self.visualize_button = tk.Button(root, text="Visualize", command=self.run_visualize)
        self.visualize_button.pack(pady=5)

        self.solve_visualize_button = tk.Button(root, text="Solve and Visualize", command=self.run_solve_and_visualize)
        self.solve_visualize_button.pack(pady=5)

        # Exit button
        self.exit_button = tk.Button(root, text="Exit", command=self.quit_app)
        self.exit_button.pack(pady=10)

        # Store file paths
        self.file_paths = {"dat": None, "mod": None, "json": None}

    def select_dat_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DAT files", "*.dat")])
        if file_path:
            self.file_paths["dat"] = file_path
            self.dat_label.config(text=f"Selected: {file_path}", fg="black")

    def select_mod_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("MOD files", "*.mod")])
        if file_path:
            self.file_paths["mod"] = file_path
            self.mod_label.config(text=f"Selected: {file_path}", fg="black")

    def select_json_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.file_paths["json"] = file_path
            self.json_label.config(text=f"Selected: {file_path}", fg="black")

    def run_solve(self):
        Thread(target=self.solve).start()

    def solve(self):
        dat_file = self.file_paths["dat"]
        mod_file = self.file_paths["mod"]
        if not dat_file or not mod_file:
            messagebox.showerror("Error", "Please select both .dat and .mod files.")
            return

        try:
            command = ["python", "solve.py", mod_file, dat_file]  # Call solve.py with the selected files
            subprocess.run(command, check=True)
            messagebox.showinfo("Success", "Solve completed successfully.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error during solve: {e}")

    def run_visualize(self):
        Thread(target=self.visualize).start()

    def visualize(self):
        json_file = self.file_paths["json"]
        if not json_file:
            messagebox.showerror("Error", "Please select a .json file.")
            return

        if not os.path.exists("evac.csv") or not os.path.exists("vehicles.csv"):
            messagebox.showerror("Error", "Required CSV files not found. Please run the solver first.")
            return

        try:
            # Start a new server with the selected JSON file
            command = ["python", "visualize.py", json_file]
            self.server_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Wait for the server to become reachable
            url = "http://127.0.0.1:8050/"
            for _ in range(30):  # Check for 15 seconds (30 x 0.5)
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        webbrowser.open_new(url)  # Open browser when ready
                        break
                except requests.ConnectionError:
                    time.sleep(0.5)

            messagebox.showinfo("Success", "Visualization started successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Error during visualization: {e}")

    def quit_app(self):
        self.terminate_server()
        self.root.quit()

    def run_solve_and_visualize(self):
        Thread(target=self.solve_and_visualize).start()

    def solve_and_visualize(self):
        if self.server_process:
            self.terminate_server()

        self.solve()
        self.visualize()

    def terminate_server(self):
        try:
            requests.post("http://127.0.0.1:8050/shutdown")
        except requests.ConnectionError:
            pass  # Server may not be running
        if self.server_process:
            self.server_process.terminate()  # Terminate if still running
            self.server_process = None


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1280x960")  # Set default window size to 1280x960
    app = FileSelectorApp(root)
    root.mainloop()

