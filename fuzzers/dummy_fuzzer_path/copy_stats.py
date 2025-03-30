import subprocess
import sys

def get_running_containers():
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to list running Docker containers.")
        sys.exit(1)
    containers = result.stdout.strip().splitlines()
    return containers

def copy_from_container(container_name):
    print(f"🔄 Copying from container: {container_name}")
    try:
        subprocess.run(["python3", "copy_out.py", container_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error copying from {container_name}: {e}")

def main():
    containers = get_running_containers()
    if not containers:
        print("No running containers found.")
        return
    for container in containers:
        copy_from_container(container)

if __name__ == "__main__":
    main()