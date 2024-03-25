
# Qdrant Snapshot Monitor

This Python script is designed to automate the monitoring of system resources (CPU, memory, and disk usage) during the upload process of a snapshot to a Qdrant vector database container. It logs resource usage before and after the upload, generates comparative charts, and verifies the successful dataset upload.

## Features

- **Automated Monitoring**: Automatically monitors and logs CPU, memory, and disk usage over time.
- **Visualization**: Produces comparative charts for visual analysis of pre and post-upload resource utilization.
- **Command-Line Simplicity**: Utilizes command-line arguments for easy operation and configuration.

## Prerequisites

Ensure you have the following installed on your system before proceeding:

- Python (version 3.6 or newer)
- Docker
- Required Python packages: `psutil`, `matplotlib`

## Installation

Follow these steps to set up the script in your environment:

1. **Clone the Repository**:
   Open your terminal and run:
   ```sh
   git clone https://github.com/ManjunathaThimmaiah/performance_monitoring.git
   cd path-to-cloned-repo
   ```

2. **Create and Activate a Python Virtual Environment** (recommended):
   ```sh
   python -m venv venv
   # For Unix/macOS
   source venv/bin/activate
   # For Windows
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   With the virtual environment activated, install the required Python packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

To execute the script, use the following command format in your terminal, replacing placeholders with actual values:
```sh
python monitor_script.py /path/to/your/snapshot_file.snapshot
```
- `monitor_script.py` should be replaced with the actual script filename.
- `/path/to/your/snapshot_file.snapshot` should be the full path to the snapshot file you wish to upload.

## Operational Flow

- Initiates system resource monitoring for a predefined time period.
- Checks for the specified Qdrant Docker container's status; starts it if not already running.
- Uploads the specified snapshot file to the Qdrant database.
- Verifies data upload success by polling the database.
- Monitors system resources again post-upload.
- Generates and saves resource usage charts to the `./charts` directory for analysis.

## Charts

Charts illustrating system resource utilization pre and post-upload are saved under the `./charts` directory. These visual aids facilitate a comparative analysis of system performance impact due to the upload process.

## Configuration

Basic script configurations can be adjusted by modifying the `container_name` and `monitor_duration` variables at the script's beginning, tailoring them to specific requirements.

