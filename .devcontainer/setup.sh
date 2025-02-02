#!/bin/bash

echo "Creating peakplay conda environment. This will take some time (minutes)"

# Ensure Conda is initialized for the current shell
eval "$(conda shell.bash hook)"

# Create the Conda environment
conda env create -f conda_env.yml -n peakplay 

# Clean up unnecessary files
conda clean -a --yes

# Initialize bashrc
conda init

# display environments
conda info --envs

# Add 'conda activate peakplay' to ~/.bashrc if not already present
if ! grep -q "conda activate peakplay" ~/.bashrc; then
    echo "Adding 'conda activate peakplay' to ~/.bashrc"
    echo -e "\n# Activate the peakplay conda environment by default\nconda activate peakplay" >> ~/.bashrc
fi

# Activate the environment
conda activate peakplay    

echo "Setup completed successfully!"
