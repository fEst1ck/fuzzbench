import subprocess
import os
import sys

if len(sys.argv) != 2:
    print("Usage: python copy_from_container.py <container_id_or_name>")
    sys.exit(1)

container_name = sys.argv[1]

# Destination directory on host
output_dir = os.path.join("output", container_name)
os.makedirs(output_dir, exist_ok=True)

# Files and directories to copy
items_to_copy = [
    "/out/corpus/command.txt",
    "/out/corpus/stats",
    "/out/corpus/crashes"
]

for item in items_to_copy:
    dest_path = os.path.join(output_dir, os.path.basename(item))
    copy_cmd = [
        "docker", "cp",
        f"{container_name}:{item}",
        dest_path
    ]
    print(f"Copying {item} to {dest_path}...")
    try:
        subprocess.run(copy_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to copy {item}: {e}")

