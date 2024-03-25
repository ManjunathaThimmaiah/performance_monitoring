import subprocess
import time
import psutil
import matplotlib.pyplot as plt
import os
import argparse  # Import argparse

# Configuration
container_name = "my_qdrant_container"
monitor_duration = 15  # seconds for pre and post monitoring

# Parse command line arguments
parser = argparse.ArgumentParser(description='Monitor system resources during Qdrant snapshot upload.')
parser.add_argument('snapshot_file', type=str, help='Path to the Qdrant snapshot file to upload.')
args = parser.parse_args()

# Use the snapshot_file from arguments
snapshot_file = args.snapshot_file
docker_command = f"docker run --name {container_name} -d -p 6333:6333 -v {os.getcwd()}/qdrant_storage:/qdrant/storage qdrant/qdrant"
upload_url = "http://localhost:6333/collections/payload/snapshots/upload"

charts_dir = "./charts"  # Directory to save charts

# Ensure the charts directory exists
os.makedirs(charts_dir, exist_ok=True)

def monitor_system_usage(duration):
    cpu_usages, memory_usages, disk_usages, timestamps = [], [], [], []
    start_time = time.time()
    while time.time() - start_time < duration:
        cpu_usages.append(psutil.cpu_percent())
        memory_usages.append(psutil.virtual_memory().percent)
        disk_usages.append(psutil.disk_usage('/').percent)
        timestamps.append(time.time() - start_time)
        time.sleep(1)
    return timestamps, cpu_usages, memory_usages, disk_usages

def plot_and_save(data, title, file_name):
    plt.figure(figsize=(10, 6))
    plt.plot(data[0], data[1], label='CPU Usage (%)')
    plt.plot(data[0], data[2], label='Memory Usage (%)', linestyle='--')
    plt.plot(data[0], data[3], label='Disk Usage (%)', linestyle='-.')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Usage (%)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(charts_dir, file_name))
    plt.close()

def check_and_start_container():
    if not subprocess.getoutput(f"docker ps -q --filter name=^{container_name}$"):
        print("Starting the Docker container...")
        subprocess.run(docker_command, shell=True)
    else:
        print("Container is already running.")

def upload_dataset():
    print("\nUploading dataset...")
    subprocess.run(f"curl -X POST '{upload_url}' -H 'Content-Type:multipart/form-data' -F 'snapshot=@{snapshot_file}'", shell=True)

def check_data_load():
    check_url = f"http://localhost:6333/collections/payload"
    while True:
        result = subprocess.run(f"curl -X GET '{check_url}' --fail -s -w '\\nHTTP Status Code: %{{http_code}}\\n'", shell=True, capture_output=True, text=True)
        if "HTTP Status Code: 200" in result.stdout:
            print("\nData loaded successfully.")
            break
        else:
            print("Waiting for data to load...")
            time.sleep(30)

# Execute monitoring and Docker operations
print("Monitoring initial system resource usage...")
pre_monitor_data = monitor_system_usage(monitor_duration)

check_and_start_container()
time.sleep(10)  # Give time for the container to warm up and start

upload_dataset()

print("Checking data load status...")
check_data_load()

print("Monitoring post data load system resource usage...")
post_monitor_data = monitor_system_usage(monitor_duration)

# Plotting and saving charts
plot_and_save(pre_monitor_data, 'Pre-Upload System Resource Usage', 'pre_upload_chart.png')
plot_and_save(post_monitor_data, 'Post-Upload System Resource Usage', 'post_upload_chart.png')
