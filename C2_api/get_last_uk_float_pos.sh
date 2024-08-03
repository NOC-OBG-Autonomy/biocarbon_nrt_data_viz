#!/bin/bash

# Execute the Python script
echo "Running Python script..."
"C:/Users/hanshil/Documents/GitHub/biocarbon_nrt_data_viz/nrt_env/Scripts/python.exe" sftp_download.py

# Check if the Python script executed successfully
if [ $? -ne 0 ]; then
    echo "Python script failed. Exiting."
    exit 1
fi

# Execute the MATLAB script
echo "Running MATLAB script..."
matlab -nodisplay -nosplash -nodesktop -r "run('C:/Users/hanshil/Documents/GitHub/biocarbon_nrt_data_viz/data/Floats/bin_files/din/parse_provor_messages.m'); exit;"

# Check if the MATLAB script executed successfully
if [ $? -ne 0 ]; then
    echo "MATLAB script failed. Exiting."
    exit 1
fi

echo "Both scripts executed successfully. Wait for matlab to process..."