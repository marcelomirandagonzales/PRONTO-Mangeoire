import time
import subprocess

# SSH details
pi_ip = '10.29.232.75'  # IP of the Raspberry Pi (eduroam)
pi_ip2 = '10.29.225.138' # IP of the second Raspberry Pi (salsa)
pi_user = 'Pronto'  # Raspberry Pi username
pi_folder_recordings = '/home/Pronto/Recordings/'
pi_folder_photos = '/home/Pronto/Photos/'
mac_folder_recordings = '/Users/marcelomiranda/Documents/IMT-L1/PRONTO/Received_recordings/'
mac_folder_photos = '/Users/marcelomiranda/Documents/IMT-L1/PRONTO/Received_photos/'

# Function to sync files using rsync
def sync_recordings():
    rsync_command = [
        'rsync', '-avz', f'Pronto@{pi_ip}:{pi_folder_recordings}', mac_folder_recordings
    ]
    subprocess.run(rsync_command)

def sync_photos():
    rsync_command = [
        'rsync', '-avz', f'Pronto@{pi_ip}:{pi_folder_photos}', mac_folder_photos
    ]
    subprocess.run(rsync_command)

# Infinite loop to check for updates every X seconds
while True:
    print("Syncing recordings...")
    sync_recordings()
    print("Recordings synced.")
    print("Syncing photos...")
    sync_photos()
    print("Photos synced.")
    time.sleep(300)  # Sleep for 5 minutes (300 seconds)


