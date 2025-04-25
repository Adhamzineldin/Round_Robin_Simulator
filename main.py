import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = -1  # -1 indicates not started yet
        self.completion_time = 0

class RoundRobinScheduler:
    def __init__(self, processes, time_quantum):
        self.processes = processes.copy()
        self.time_quantum = time_quantum
        self.gantt_chart = []
        self.current_time = 0

    def run(self):
        # Sort processes by arrival time
        self.processes.sort(key=lambda x: x.arrival_time)

        ready_queue = []
        remaining_processes = len(self.processes)
        process_index = 0

        # Continue until all processes are complete
        while remaining_processes > 0:
            # Add arriving processes to the ready queue
            while process_index < len(self.processes) and self.processes[process_index].arrival_time <= self.current_time:
                ready_queue.append(self.processes[process_index])
                process_index += 1

            if not ready_queue:  # If no process is ready, advance time
                self.gantt_chart.append(("Idle", self.current_time, self.processes[process_index].arrival_time))
                self.current_time = self.processes[process_index].arrival_time
                continue

            # Get the next process from the ready queue
            current_process = ready_queue.pop(0)

            # If this is the first time the process is running, set response time
            if current_process.response_time == -1:
                current_process.response_time = self.current_time - current_process.arrival_time

            # Determine how long this process will run
            run_time = min(self.time_quantum, current_process.remaining_time)

            # Add to Gantt chart
            self.gantt_chart.append((f"P{current_process.pid}", self.current_time, self.current_time + run_time))

            # Update current time
            self.current_time += run_time

            # Update remaining time for the process
            current_process.remaining_time -= run_time

            # Add new arriving processes to the ready queue
            while process_index < len(self.processes) and self.processes[process_index].arrival_time <= self.current_time:
                ready_queue.append(self.processes[process_index])
                process_index += 1

            # If the process is not finished, put it back in the ready queue
            if current_process.remaining_time > 0:
                ready_queue.append(current_process)
            else:
                # Process is complete
                remaining_processes -= 1
                current_process.completion_time = self.current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time

        return self.gantt_chart

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Round Robin CPU Scheduler Simulation")
        self.geometry("1200x800")
        self.processes = []

        self.create_widgets()

    def create_widgets(self):
        # Create a notebook (tabbed interface)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create the "Input" tab
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="Input")

        # Create the "Output" tab
        self.output_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.output_frame, text="Output")

        # Set up the Input tab
        self.setup_input_tab()

        # Set up the Output tab
        self.setup_output_tab()

    def setup_input_tab(self):
        # Number of processes
        ttk.Label(self.input_frame, text="Number of Processes:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.num_processes_var = tk.StringVar()
        num_processes_entry = ttk.Entry(self.input_frame, textvariable=self.num_processes_var)
        num_processes_entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W)

        # Time Quantum
        ttk.Label(self.input_frame, text="Time Quantum:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.time_quantum_var = tk.StringVar()
        time_quantum_entry = ttk.Entry(self.input_frame, textvariable=self.time_quantum_var)
        time_quantum_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        # Button to generate process input fields
        ttk.Button(self.input_frame, text="Generate Process Fields", command=self.generate_process_fields).grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # Frame for process input fields
        self.process_frame = ttk.Frame(self.input_frame)
        self.process_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E+tk.N+tk.S)

        # Button to run simulation
        self.run_button = ttk.Button(self.input_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        self.run_button["state"] = "disabled"

    def setup_output_tab(self):
        # Frame for results table
        self.results_frame = ttk.LabelFrame(self.output_frame, text="Process Results")
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollable results table
        self.results_tree = ttk.Treeview(self.results_frame)
        self.results_tree["columns"] = ("PID", "Arrival Time", "Burst Time", "Completion Time",
                                        "Turnaround Time", "Waiting Time", "Response Time")

        # Configure columns
        self.results_tree.column("#0", width=0, stretch=tk.NO)
        for col in self.results_tree["columns"]:
            self.results_tree.column(col, anchor=tk.CENTER, width=120)
            self.results_tree.heading(col, text=col, anchor=tk.CENTER)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame for average metrics
        self.avg_frame = ttk.LabelFrame(self.output_frame, text="Average Metrics")
        self.avg_frame.pack(fill=tk.X, padx=10, pady=10)

        # Average metrics labels
        self.avg_turnaround_var = tk.StringVar()
        self.avg_waiting_var = tk.StringVar()
        self.avg_response_var = tk.StringVar()

        ttk.Label(self.avg_frame, text="Average Turnaround Time:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.avg_frame, textvariable=self.avg_turnaround_var).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.avg_frame, text="Average Waiting Time:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.avg_frame, textvariable=self.avg_waiting_var).grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        ttk.Label(self.avg_frame, text="Average Response Time:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(self.avg_frame, textvariable=self.avg_response_var).grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        # Frame for Gantt chart
        self.gantt_frame = ttk.LabelFrame(self.output_frame, text="Gantt Chart")
        self.gantt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def generate_process_fields(self):
        # Clear previous process fields
        for widget in self.process_frame.winfo_children():
            widget.destroy()

        # Validate input
        try:
            num_processes = int(self.num_processes_var.get())
            if num_processes <= 0:
                messagebox.showerror("Invalid Input", "Number of processes must be positive.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Number of processes must be a number.")
            return

        try:
            time_quantum = int(self.time_quantum_var.get())
            if time_quantum <= 0:
                messagebox.showerror("Invalid Input", "Time quantum must be positive.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Time quantum must be a number.")
            return

        # Create headers
        ttk.Label(self.process_frame, text="Process ID").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.process_frame, text="Arrival Time").grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(self.process_frame, text="Burst Time").grid(row=0, column=2, padx=10, pady=5)

        # Create entry fields for each process
        self.arrival_time_vars = []
        self.burst_time_vars = []

        for i in range(num_processes):
            ttk.Label(self.process_frame, text=f"P{i}").grid(row=i+1, column=0, padx=10, pady=5)

            arrival_time_var = tk.StringVar()
            arrival_time_entry = ttk.Entry(self.process_frame, textvariable=arrival_time_var)
            arrival_time_entry.grid(row=i+1, column=1, padx=10, pady=5)
            self.arrival_time_vars.append(arrival_time_var)

            burst_time_var = tk.StringVar()
            burst_time_entry = ttk.Entry(self.process_frame, textvariable=burst_time_var)
            burst_time_entry.grid(row=i+1, column=2, padx=10, pady=5)
            self.burst_time_vars.append(burst_time_var)

        self.run_button["state"] = "normal"

    def validate_process_inputs(self):
        processes = []

        for i in range(len(self.arrival_time_vars)):
            try:
                arrival_time = int(self.arrival_time_vars[i].get())
                if arrival_time < 0:
                    messagebox.showerror("Invalid Input", f"Arrival time for P{i} must be non-negative.")
                    return None
            except ValueError:
                messagebox.showerror("Invalid Input", f"Arrival time for P{i} must be a number.")
                return None

            try:
                burst_time = int(self.burst_time_vars[i].get())
                if burst_time <= 0:
                    messagebox.showerror("Invalid Input", f"Burst time for P{i} must be positive.")
                    return None
            except ValueError:
                messagebox.showerror("Invalid Input", f"Burst time for P{i} must be a number.")
                return None

            processes.append(Process(i, arrival_time, burst_time))

        return processes

    def run_simulation(self):
        # Validate and collect process data
        processes = self.validate_process_inputs()
        if processes is None:
            return

        # Get time quantum
        time_quantum = int(self.time_quantum_var.get())

        # Run the scheduler
        scheduler = RoundRobinScheduler(processes, time_quantum)
        gantt_chart = scheduler.run()

        # Display results
        self.display_results(processes, gantt_chart)

        # Switch to the output tab
        self.notebook.select(self.output_frame)

    def display_results(self, processes, gantt_chart):
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        # Add process results to the table
        for p in processes:
            self.results_tree.insert("", tk.END, values=(
                    f"P{p.pid}", p.arrival_time, p.burst_time,
                    p.completion_time, p.turnaround_time,
                    p.waiting_time, p.response_time
            ))

        # Calculate and display average metrics
        avg_turnaround = sum(p.turnaround_time for p in processes) / len(processes)
        avg_waiting = sum(p.waiting_time for p in processes) / len(processes)
        avg_response = sum(p.response_time for p in processes) / len(processes)

        self.avg_turnaround_var.set(f"{avg_turnaround:.2f}")
        self.avg_waiting_var.set(f"{avg_waiting:.2f}")
        self.avg_response_var.set(f"{avg_response:.2f}")

        # Create Gantt chart
        self.create_gantt_chart(gantt_chart)

    def create_gantt_chart(self, gantt_chart):
        # Clear previous Gantt chart
        for widget in self.gantt_frame.winfo_children():
            widget.destroy()

        # Create figure and axis
        fig = Figure(figsize=(10, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Plot Gantt chart
        y_ticks = []
        y_labels = []

        for i, (process, start, end) in enumerate(gantt_chart):
            ax.barh(i, end - start, left=start, height=0.5,
                    align='center', color='blue' if process != "Idle" else 'lightgray',
                    edgecolor='black', alpha=0.8)

            # Add process label in the middle of the bar
            ax.text((start + end) / 2, i, process,
                    ha='center', va='center', color='white', fontweight='bold')

            y_ticks.append(i)
            y_labels.append(process)

        # Set labels and ticks
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.set_xlabel('Time')
        ax.set_title('Gantt Chart')

        # Add vertical lines and time labels
        time_points = sorted(set([event[1] for event in gantt_chart] + [event[2] for event in gantt_chart]))
        for time in time_points:
            ax.axvline(x=time, color='gray', linestyle='--', alpha=0.3)
            ax.text(time, -0.5, str(time), ha='center', va='top')

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.gantt_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = Application()
    app.mainloop()