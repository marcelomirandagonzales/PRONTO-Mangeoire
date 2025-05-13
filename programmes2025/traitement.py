import os
import time
import subprocess

# Your local recordings folder
local_folder = '/Users/marcelomiranda/Documents/IMT-L1/PRONTO/Received_recordings'
# File where we keep track of processed files
processed_log = '/Users/marcelomiranda/Documents/IMT-L1/PRONTO/processed_files.txt'

def load_processed_files():
    if not os.path.exists(processed_log):
        return set()
    with open(processed_log, 'r') as f:
        return set(line.strip() for line in f)

def save_processed_file(filename):
    with open(processed_log, 'a') as f:
        f.write(filename + '\n')

def process_new_files():
    processed_files = load_processed_files()
    all_files = set(os.listdir(local_folder))

    new_files = all_files - processed_files

    for file in new_files:
        full_path = os.path.join(local_folder, file)

        if os.path.isfile(full_path):
            # Your custom operation goes here
            if file.endswith('.flac'):
                # Process the file
                print(f"Processing {file}...")

                path_recordings = f"/Users/marcelomiranda/Documents/IMT-L1/PRONTO/Received_recordings/{file}"
                path_results = f"/Users/marcelomiranda/Documents/IMT-L1/PRONTO/Results/{file}.selection.table.txt"
                path_analyze = "/Users/marcelomiranda/Documents/IMT-L1/PRONTO/Mangeoire/birdnet_analyzer/analyze.py"

                cmd = ["python3", path_analyze, "--i", path_recordings, "--o", path_results]
                result = subprocess.run(cmd, capture_output=True, text=True)

                # Mark as processed
                save_processed_file(file)
                print(f"Processed {file}: {result.stdout}")


            # Mark as processed
            save_processed_file(file)

# Example: Run processing after every sync
while True:
    print("Checking for new files...")
    process_new_files()
    time.sleep(20)  # every 5 mins
