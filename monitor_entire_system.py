import subprocess
import time
import psutil
import matplotlib.pyplot as plt
import os
import argparse
import threading

# Argument parsing
parser = argparse.ArgumentParser(description="Monitor system resources and upload data.")
parser.add_argument('--snapshot_file', type=str, required=True, help='Path to the snapshot file to upload.')
parser.add_argument('--pre_post_monitor_duration', type=int, default=10, help='Duration (in seconds) for pre and post monitoring.')
args = parser.parse_args()

# Configuration based on parsed arguments
snapshot_file = args.snapshot_file
monitor_duration = args.pre_post_monitor_duration

container_name = "my_qdrant_container"
docker_command = f"docker run --name {container_name} -d -p 6333:6333 -v {os.getcwd()}/qdrant_storage:/qdrant/storage qdrant/qdrant"
upload_url = "http://localhost:6333/collections/payload/snapshots/upload"

charts_dir = "./charts"  # Directory to save charts

# Ensure the charts directory exists
os.makedirs(charts_dir, exist_ok=True)

def monitor_system_usage(duration, continuous=False):
    """Monitor and record system usage."""
    cpu_usages, memory_usages, disk_usages, timestamps = [], [], [], []
    start_time = time.time()
    while continuous or time.time() - start_time < duration:
        cpu_usages.append(psutil.cpu_percent(interval=1))
        memory_usages.append(psutil.virtual_memory().percent)
        disk_usages.append(psutil.disk_usage('/').percent)
        timestamps.append(time.time() - start_time)
        if continuous and stop_event.is_set():
            break
    return timestamps, cpu_usages, memory_usages, disk_usages

def plot_and_save(data, title, file_name):
    """Plot and save the data."""
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
    """Check if the container is running and start it if not."""
    if not subprocess.getoutput(f"docker ps -q --filter name=^{container_name}$"):
        print("Starting the Docker container...")
        subprocess.run(docker_command, shell=True)
    else:
        print("Container is already running.")

def upload_dataset():
    """Upload the dataset."""
    curl_command = f"curl -X POST '{upload_url}' -H 'Content-Type:multipart/form-data' -F 'snapshot=@{snapshot_file}'"
    print("\nUploading dataset...")
    subprocess.run(curl_command, shell=True)

def check_data_load():
    """Check the status of the data load."""
    check_url = f"http://localhost:6333/collections/payload"
    while True:
        result = subprocess.run(f"curl -X GET '{check_url}' --fail -s -w '\\nHTTP Status Code: %{{http_code}}\\n'", shell=True, capture_output=True, text=True)
        if "HTTP Status Code: 200" in result.stdout:
            print("\nData loaded successfully.")
            break
        else:
            print("Waiting for data to load...")
            time.sleep(30)

# Monitoring control for parallel execution
stop_event = threading.Event()

def start_monitoring_during_load():
    """Start a thread for continuous monitoring."""
    stop_event.clear()
    monitoring_thread = threading.Thread(target=monitor_system_usage, args=(None, True), daemon=True)
    monitoring_thread.start()
    return monitoring_thread

def stop_monitoring_during_load():
    """Signal the monitoring thread to stop."""
    stop_event.set()

# Main execution
if __name__ == "__main__":
    print("Monitoring initial system resource usage...")
    pre_monitor_data = monitor_system_usage(monitor_duration)

    check_and_start_container()
    time.sleep(10)  # Give time for the container to start

    monitoring_thread = start_monitoring_during_load()

    upload_dataset()

    print("Checking data load status...")
    check_data_load()

    # Stop monitoring during data load
    stop_monitoring_during_load()
    monitoring_thread.join()

    print("Monitoring post data load system resource usage...")
    post_monitor_data = monitor_system_usage(monitor_duration)

    # Plotting and saving charts
    plot_and_save(pre_monitor_data, 'Pre-Upload System Resource Usage', 'pre_upload_chart.png')
    plot_and_save(post_monitor_data, 'Post-Upload System Resource Usage', 'post_upload_chart.png')
