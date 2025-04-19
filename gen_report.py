import os
import sys
import json
import matplotlib.pyplot as plt
from datetime import datetime

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

def generate_instance_report(container_name, instance_name, output_dir):
    container_dir = os.path.join(output_dir, container_name)
    instance_dir = os.path.join(container_dir, instance_name)
    stats_path = os.path.join(instance_dir, "stats", "fuzzer_log.json")
    cmd_path = os.path.join(instance_dir, "command.txt")
    report_path = os.path.join(instance_dir, "report.html")

    if not os.path.exists(stats_path):
        print(f"[!] Stats not found for {container_name}/{instance_name}")
        return

    # Load stats JSON
    with open(stats_path, "r") as f:
        stats = json.load(f)

    # Load command
    command = "(unknown)"
    if os.path.exists(cmd_path):
        with open(cmd_path, "r") as f:
            command = f.read().strip()

    # Extract metrics
    time = [entry["runtime_seconds"] for entry in stats]
    coverage_block = [entry["coverage_count"]["block"] for entry in stats]
    coverage_edge = [entry["coverage_count"]["edge"] for entry in stats]
    coverage_path = [entry["coverage_count"]["path"] for entry in stats]
    executions = [entry["total_executions"] for entry in stats]
    queue_size = [entry["queue_size"] for entry in stats]
    crash_count = [entry["crash_count"] for entry in stats]

    # Final state
    final = stats[-1]
    final_state_html = f"""
    <h2>Final Fuzzer State</h2>
    <ul>
        <li><strong>Runtime:</strong> {final['runtime_seconds']} seconds</li>
        <li><strong>Total Executions:</strong> {final['total_executions']}</li>
        <li><strong>Queue Size:</strong> {final['queue_size']}</li>
        <li><strong>Crashes:</strong> {final['crash_count']}</li>
        <li><strong>Block Coverage:</strong> {final['coverage_count']['block']}</li>
        <li><strong>Edge Coverage:</strong> {final['coverage_count']['edge']}</li>
        <li><strong>Path Coverage:</strong> {final['coverage_count']['path']}</li>
    </ul>
    """

    # Plot files
    plots = []
    def save_plot(data, title, ylabel, name):
        filename = os.path.join(instance_dir, f"{name}.png")
        plot_metric(time, data, title, ylabel, filename)
        plots.append((title, os.path.basename(filename)))

    save_plot(coverage_block, "Block Coverage Over Time", "Block Coverage", "block_coverage")
    save_plot(coverage_edge, "Edge Coverage Over Time", "Edge Coverage", "edge_coverage")
    save_plot(coverage_path, "Path Coverage Over Time", "Path Coverage", "path_coverage")
    save_plot(executions, "Total Executions Over Time", "Executions", "executions")
    save_plot(queue_size, "Queue Size Over Time", "Queue Size", "queue_size")
    save_plot(crash_count, "Crash Count Over Time", "Crash Count", "crash_count")

    # Write HTML
    with open(report_path, "w") as f:
        f.write(f"<html><head><title>Fuzzing Report: {container_name}/{instance_name}</title></head><body>")
        f.write(f"<h1>Fuzzing Report: {container_name}/{instance_name}</h1>")
        f.write(f"<p><strong>Fuzzing command:</strong> <code>{command}</code></p>")
        f.write(f"<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        f.write(final_state_html)
        for title, img_file in plots:
            f.write(f"<h2>{title}</h2>")
            f.write(f"<img src='{img_file}' style='max-width:800px'><br><br>")
        f.write("</body></html>")

    print(f"[✓] Report generated: {report_path}")

def generate_report(container_name, output_dir):
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

    # Generate report for each instance
    for instance in instances:
        print(f"📊 Generating report for: {container_name}/{instance}")
        generate_instance_report(container_name, instance, output_dir)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_html_report.py <container_name> <output_dir>")
        sys.exit(1)

    container_name = sys.argv[1]
    output_dir = sys.argv[2]
    generate_report(container_name, output_dir)