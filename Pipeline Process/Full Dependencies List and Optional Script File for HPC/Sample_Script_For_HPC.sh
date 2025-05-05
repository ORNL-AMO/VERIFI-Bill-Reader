#!/bin/bash
#SBATCH --job-name=       
#SBATCH --output=      
#SBATCH --error=       
#SBATCH --mem=                  
#SBATCH --gpus=                 
#SBATCH --cpus-per-task=          
#SBATCH --time=    
#SBATCH --account=

# Ensure Ollama is running
killall ollama

export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MODELS=/MY_OLLAMA_MODELS_DIR

# ./MY_DIR/bin/ollama serve
./MY_DIR/ollama serve & 

sleep 10

# If there are issues with dependencies on the system use a variation of:
source /opt/ohpc/pub/spack/v0.23.0/share/spack/setup-env.sh
spack load numpy py-torch

# Activate Virtual Environment
source test/bin/activate

# Use for first install
pip install -r requirements.txt

# Run program
python /MY_DIR/pipeline.py
