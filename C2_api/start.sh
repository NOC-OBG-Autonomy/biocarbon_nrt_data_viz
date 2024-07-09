#!/bin/sh

# Infinite loop to run the script every 20 minutes
while true
do
    python update_kml.py
    sleep 1200  # Sleep for 1200 seconds (20 minutes)
done