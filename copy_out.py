import subprocess
import os
import sys
import shutil

if len(sys.argv) != 2:
    print("Usage: python copy_from_container.py <container_id_or_name>")
    sys.exit(1)

container_name = sys.argv[1]

# Destination directory on host
output_dir = os.path.join("output", container_name)
os.makedirs(output_dir, exist_ok=True)

# Files to copy from each instance directory
files_to_copy = [
    "command.txt",
    "stats",
    "crashes"
]

def copy_instance_files(instance_path, dest_base):
    """Copy files from a single instance directory."""
    instance_name = os.path.basename(instance_path)
    instance_dest = os.path.join(dest_base, instance_name)
    os.makedirs(instance_dest, exist_ok=True)
    
    for file_name in files_to_copy:
        src_path = os.path.join(instance_path, file_name)
        dest_path = os.path.join(instance_dest, file_name)
        
        # Remove existing destination if it exists
        if os.path.exists(dest_path):
            if os.path.isdir(dest_path):
                shutil.rmtree(dest_path)
            else:
                os.remove(dest_path)
                
        copy_cmd = [
            "docker", "cp",
            f"{container_name}:{src_path}",
            dest_path
        ]
        print(f"Copying {src_path} to {dest_path}...")
        try:
            subprocess.run(copy_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[!] Failed to copy {src_path}: {e}")

# Get all instance directories
list_cmd = ["docker", "exec", container_name, "ls", "/out/corpus"]
try:
    result = subprocess.run(list_cmd, capture_output=True, text=True, check=True)
    instances = [line for line in result.stdout.splitlines() if line.startswith("instance_")]
    
    if not instances:
        print("No instance directories found in /out/corpus")
        sys.exit(1)
        
    for instance in instances:
        instance_path = os.path.join("/out/corpus", instance)
        copy_instance_files(instance_path, output_dir)
        
except subprocess.CalledProcessError as e:
    print(f"[!] Failed to list instance directories: {e}")
    sys.exit(1)

