

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
