import os
import sys
import json
import matplotlib
matplotlib.use("Agg")
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

def generate_instance_report(result_dir, instance_name):
    # Determine if this is single instance or multi-instance
    if instance_name is None:
        # Single instance: stats directly in result directory
        instance_dir = result_dir
        stats_path = os.path.join(instance_dir, "stats", "fuzzer_log.json")
        cmd_path = os.path.join(instance_dir, "command.txt")
        report_path = os.path.join(instance_dir, "report.html")
        title = os.path.basename(result_dir)
    else:
        # Multi-instance: stats in instance subdirectory
        instance_dir = os.path.join(result_dir, instance_name)
        stats_path = os.path.join(instance_dir, "stats", "fuzzer_log.json")
        cmd_path = os.path.join(instance_dir, "command.txt")
        report_path = os.path.join(instance_dir, "report.html")
        title = f"{os.path.basename(result_dir)}/{instance_name}"

    if not os.path.exists(stats_path):
        if instance_name is None:
            print(f"[!] Stats not found for {os.path.basename(result_dir)}")
        else:
            print(f"[!] Stats not found for {os.path.basename(result_dir)}/{instance_name}")
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
    coverage_pfp = [entry["coverage_count"]["pfp"] for entry in stats]
    coverage_rawpath = [entry["coverage_count"]["rawpath"] for entry in stats]
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
        <li><strong>PFP Coverage:</strong> {final['coverage_count']['pfp']}</li>
        <li><strong>Raw Path Coverage:</strong> {final['coverage_count']['rawpath']}</li>
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
    save_plot(coverage_pfp, "Path Coverage Over Time", "PFP Coverage", "pfp_coverage")
    save_plot(coverage_rawpath, "Raw Path Coverage Over Time", "Raw Path Coverage", "rawpath_coverage")
    save_plot(executions, "Total Executions Over Time", "Executions", "executions")
    save_plot(queue_size, "Queue Size Over Time", "Queue Size", "queue_size")
    save_plot(crash_count, "Crash Count Over Time", "Crash Count", "crash_count")

    # Write HTML
    with open(report_path, "w") as f:
        f.write(f"<html><head><title>Fuzzing Report: {result_dir}/{instance_name}</title></head><body>")
        f.write(f"<h1>Fuzzing Report: {result_dir}/{instance_name}</h1>")
        f.write(f"<p><strong>Fuzzing command:</strong> <code>{command}</code></p>")
        f.write(f"<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        f.write(final_state_html)
        for title, img_file in plots:
            f.write(f"<h2>{title}</h2>")
            f.write(f"<img src='{img_file}' style='max-width:800px'><br><br>")
        f.write("</body></html>")

    print(f"[✓] Report generated: {report_path}")

def generate_report(result_dir):
    if not os.path.exists(result_dir):
        print(f"[!] Result directory '{result_dir}' does not exist.")
        sys.exit(1)

    # Check if this is a single instance format (stats directly in result directory)
    single_instance_stats = os.path.join(result_dir, "stats", "fuzzer_log.json")
    if os.path.exists(single_instance_stats):
        print(f"📊 Detected single instance format for: {os.path.basename(result_dir)}")
        generate_instance_report(result_dir, None)
        return

    # Check for multi-instance format
    instances = [
        d for d in os.listdir(result_dir)
        if os.path.isdir(os.path.join(result_dir, d)) and d.startswith("instance_")
    ]

    if not instances:
        print(f"[!] No instance directories found in {result_dir}")
        return

    # Generate report for each instance
    for instance in instances:
        print(f"📊 Generating report for: {os.path.basename(result_dir)}/{instance}")
        generate_instance_report(result_dir, instance)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        # Single instance case: only result_dir provided
        result_dir = sys.argv[1]
        generate_report(result_dir)
    else:
        print("Usage: gen_report.py <result_dir>")
        sys.exit(1)
