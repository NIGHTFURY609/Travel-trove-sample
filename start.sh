#!/bin/bash

echo "Starting Python scripts..."


# Run Python scripts in the background
gunicorn -w 4 -b 0.0.0.0:5000 app:app &
gunicorn -w 4 -b 0.0.0.0:5001 call:app &
gunicorn -w 4 -b 0.0.0.0:5002 server:app &
echo "All scripts started!"
wait  # Ensures the script keeps running
