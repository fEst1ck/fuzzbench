import os
import subprocess

def generate_all_reports(output_dir="output"):
    if not os.path.exists(output_dir):
        print(f"[!] Output directory '{output_dir}' does not exist.")
        return

    container_dirs = [
        d for d in os.listdir(output_dir)
        if os.path.isdir(os.path.join(output_dir, d))
    ]

    if not container_dirs:
        print("[!] No container directories found in output/")
        return

    for container_name in container_dirs:
        print(f"📊 Generating report for: {container_name}")
        try:
            subprocess.run(
                ["python3", "gen_report.py", container_name, output_dir],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to generate report for {container_name}: {e}")

if __name__ == "__main__":
    generate_all_reports()