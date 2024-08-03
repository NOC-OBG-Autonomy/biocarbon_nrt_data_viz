import pysftp
from tqdm import tqdm
import os
# Define your SFTP server credentials
hostname = 'rudics.thorium.cls.fr'
username = 'nocbio010b'
password = 'HOcopojes'



# Optional: Define known hosts file or disable host key checking (not recommended for production)
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None  # Disable host key checking

# Connect to the SFTP server
with pysftp.Connection(host=hostname, username=username, password=password, cnopts=cnopts) as sftp:
    print("Connection successfully established...")

    # Example: List files in the root directory
    file_list = sftp.listdir()
    file_saved = os.listdir("C:/Users/hanshil/Documents/GitHub/biocarbon_nrt_data_viz/data/Floats/bin_files/din/")

    files = [ f for f in file_list if f not in file_saved] 
    files = [ f for f in files if f not in ['backups', 'logs']] 
    
    if not files:
        print('There isn\'t any new data')
    else :

        # Example: Download a file
        for file in tqdm(files):
            sftp.get(file, 'C:/Users/hanshil/Documents/GitHub/biocarbon_nrt_data_viz/data/Floats/bin_files/din/' + str(file))
        #remote_file_path = '/remote/path/to/your/file'
        # local_file_path = '/local/path/to/save/your/file'
        # sftp.get(remote_file_path, local_file_path)

        # Example: Upload a file
        # sftp.put(local_file_path, remote_file_path)
    print('sftp operation done')