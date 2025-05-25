import os
import subprocess
import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

def plot_metric(x, y, title, ylabel, filename):
    plt.figure()
    plt.plot(x, y)
    plt.xlabel("Runtime (s)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def generate_average_report(container_name, output_dir):
    """Generate a report showing averages across all instances of a container."""
    container_dir = os.path.join(output_dir, container_name)
    if not os.path.exists(container_dir):
        print(f"[!] Container directory '{container_dir}' does not exist.")
        return

    # Find all instance directories
    instances = [
        d for d in os.listdir(container_dir)
        if os.path.isdir(os.path.join(container_dir, d)) and d.startswith("instance_")
    ]

    if not instances:
        print(f"[!] No instance directories found in {container_dir}")
        return

    # Get command from first instance (they should all be the same)
    command = "(unknown)"
    first_instance = instances[0]
    cmd_path = os.path.join(container_dir, first_instance, "command.txt")
    if os.path.exists(cmd_path):
        with open(cmd_path, "r") as f:
            command = f.read().strip()

    # Collect stats from all instances
    all_stats = []
    for instance in instances:
        stats_path = os.path.join(container_dir, instance, "stats", "fuzzer_log.json")
        if not os.path.exists(stats_path):
            print(f"[!] Stats not found for {container_name}/{instance}")
            continue
        
        with open(stats_path, "r") as f:
            all_stats.append(json.load(f))

    if not all_stats:
        print(f"[!] No valid stats found for {container_name}")
        return

    # Find the maximum runtime across all instances
    max_runtime = max(max(entry["runtime_seconds"] for entry in stats) for stats in all_stats)
    
    # Create time points for interpolation
    time_points = np.linspace(0, max_runtime, 100)
    
    # Initialize arrays for averaged metrics
    avg_coverage_block = np.zeros_like(time_points)
    avg_coverage_edge = np.zeros_like(time_points)
    avg_coverage_path = np.zeros_like(time_points)
    avg_coverage_pfp = np.zeros_like(time_points)
    avg_executions = np.zeros_like(time_points)
    avg_queue_size = np.zeros_like(time_points)
    avg_crash_count = np.zeros_like(time_points)
    
    # Interpolate and average metrics across instances
    for stats in all_stats:
        times = np.array([entry["runtime_seconds"] for entry in stats])
        metrics = {
            "block": np.array([entry["coverage_count"]["block"] for entry in stats]),
            "edge": np.array([entry["coverage_count"]["edge"] for entry in stats]),
            "path": np.array([entry["coverage_count"]["path"] for entry in stats]),
            "pfp": np.array([entry["coverage_count"]["pfp"] for entry in stats]),
            "executions": np.array([entry["total_executions"] for entry in stats]),
            "queue_size": np.array([entry["queue_size"] for entry in stats]),
            "crash_count": np.array([entry["crash_count"] for entry in stats])
        }
        
        for metric_name, values in metrics.items():
            interpolated = np.interp(time_points, times, values)
            if metric_name == "block":
                avg_coverage_block += interpolated
            elif metric_name == "edge":
                avg_coverage_edge += interpolated
            elif metric_name == "path":
                avg_coverage_path += interpolated
            elif metric_name == "pfp":
                avg_coverage_pfp += interpolated
            elif metric_name == "executions":
                avg_executions += interpolated
            elif metric_name == "queue_size":
                avg_queue_size += interpolated
            elif metric_name == "crash_count":
                avg_crash_count += interpolated

    # Calculate averages
    n_instances = len(all_stats)
    avg_coverage_block /= n_instances
    avg_coverage_edge /= n_instances
    avg_coverage_path /= n_instances
    avg_coverage_pfp /= n_instances
    avg_executions /= n_instances
    avg_queue_size /= n_instances
    avg_crash_count /= n_instances

    # Create average report directory
    avg_report_dir = os.path.join(container_dir, "average_report")
    os.makedirs(avg_report_dir, exist_ok=True)

    # Generate plots
    plots = []
    def save_plot(data, title, ylabel, name):
        filename = os.path.join(avg_report_dir, f"{name}.png")
        plot_metric(time_points, data, title, ylabel, filename)
        plots.append((title, os.path.basename(filename)))

    save_plot(avg_coverage_block, "Average Block Coverage Over Time", "Block Coverage", "avg_block_coverage")
    save_plot(avg_coverage_edge, "Average Edge Coverage Over Time", "Edge Coverage", "avg_edge_coverage")
    save_plot(avg_coverage_path, "Average Path Coverage Over Time", "Path Coverage", "avg_path_coverage")
    save_plot(avg_coverage_pfp, "Average PFP Coverage Over Time", "PFP Coverage", "avg_pfp_coverage")
    save_plot(avg_executions, "Average Total Executions Over Time", "Executions", "avg_executions")
    save_plot(avg_queue_size, "Average Queue Size Over Time", "Queue Size", "avg_queue_size")
    save_plot(avg_crash_count, "Average Crash Count Over Time", "Crash Count", "avg_crash_count")

    # Calculate final averages
    final_metrics = {
        "runtime_seconds": max_runtime,
        "total_executions": avg_executions[-1],
        "queue_size": avg_queue_size[-1],
        "crash_count": avg_crash_count[-1],
        "coverage_count": {
            "block": avg_coverage_block[-1],
            "edge": avg_coverage_edge[-1],
            "path": avg_coverage_path[-1],
            "pfp": avg_coverage_pfp[-1]
        }
    }

    # Write HTML report
    report_path = os.path.join(avg_report_dir, "average_report.html")
    with open(report_path, "w") as f:
        f.write(f"<html><head><title>Average Fuzzing Report: {container_name}</title></head><body>")
        f.write(f"<h1>Average Fuzzing Report: {container_name}</h1>")
        f.write(f"<p><strong>Number of instances averaged:</strong> {n_instances}</p>")
        f.write(f"<p><strong>Fuzzing command:</strong> <code>{command}</code></p>")
        f.write(f"<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        # Final state
        f.write("""
        <h2>Average Final Fuzzer State</h2>
        <ul>
            <li><strong>Runtime:</strong> {:.2f} seconds</li>
            <li><strong>Total Executions:</strong> {:.2f}</li>
            <li><strong>Queue Size:</strong> {:.2f}</li>
            <li><strong>Crashes:</strong> {:.2f}</li>
            <li><strong>Block Coverage:</strong> {:.2f}</li>
            <li><strong>Edge Coverage:</strong> {:.2f}</li>
            <li><strong>Path Coverage:</strong> {:.2f}</li>
            <li><strong>PFP Coverage:</strong> {:.2f}</li>
        </ul>
        """.format(
            final_metrics["runtime_seconds"],
            final_metrics["total_executions"],
            final_metrics["queue_size"],
            final_metrics["crash_count"],
            final_metrics["coverage_count"]["block"],
            final_metrics["coverage_count"]["edge"],
            final_metrics["coverage_count"]["path"],
            final_metrics["coverage_count"]["pfp"]
        ))

        # Add plots
        for title, img_file in plots:
            f.write(f"<h2>{title}</h2>")
            f.write(f"<img src='{img_file}' style='max-width:800px'><br><br>")
        
        f.write("</body></html>")

    print(f"[✓] Average report generated: {report_path}")

def generate_all_reports(output_dir="output"):
    if not os.path.exists(output_dir):
        print(f"[!] Output directory '{output_dir}' does not exist.")
        return

    # Find all container directories
    container_dirs = [
        d for d in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, d))
    ]

    if not container_dirs:
        print("[!] No container directories found in output/")
        return

    for container_name in container_dirs:
        print(f"\n📊 Processing container: {container_name}")
        try:
            # Generate individual instance reports
            subprocess.run(
                ["python3", "gen_report.py", container_name, output_dir],
                check=True
            )
            # Generate average report
            generate_average_report(container_name, output_dir)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to generate reports for {container_name}: {e}")

if __name__ == "__main__":
    generate_all_reports()