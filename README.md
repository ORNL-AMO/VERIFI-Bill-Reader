# Setting Up PDF to Excel Pipeline on an HPC Environment

This guide explains how to run the `pipeline.py` script, which converts PDFs to formatted Excel files, in a High-Performance Computing (HPC) environment using [Ollama](https://ollama.com/) and [Surya OCR](https://github.com/VikParuchuri/surya).

>  **Note:** This assumes you have already installed Ollama and configured your HPC system. If not, please refer to the **"Setting Up Marker and Ollama Environment on HPC"** documentation.

## Overview

- The `pipeline.py` script is designed to run via a batch job (e.g., `sbatch`), but it can also be executed manually.
- Input PDF files should be placed in the `raw` folder.
- Processed Excel files will be saved in the `excel_output` folder.
- The pipeline uses AI extraction with configuration files and prompt templates for flexibility.

## Sample `sbatch` Script

```bash
#!/bin/bash
#SBATCH --job-name=pdf_to_excel
#SBATCH --output=job_output.log
#SBATCH --error=job_error.log
#SBATCH --mem=16G
#SBATCH --gpus=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --account=my_account

killall ollama

export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MODELS=/path/to/your/ollama_models

/path/to/ollama serve &
sleep 10

source /opt/ohpc/pub/spack/v0.23.0/share/spack/setup-env.sh
spack load numpy py-torch

source /path/to/venv/bin/activate

pip install -r requirements.txt

python /path/to/pipeline.py
```

## Setup Steps

1. **Install Ollama**  
   From [ollama.com](https://ollama.com) or use binaries compatible with your system.

2. **Set up virtual environment**  
   ```bash
   python3 -m venv test
   source test/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```
   Note: If there are any issues try using `spack load`. 

4. **Set environment variables**  
   ```bash
   export OLLAMA_MODELS=/path/to/ollama_models
   ollama serve &
   ```

5. **Edit configuration files**  
   - `config.json`: General settings
   		-    `use_marker_ocr`   - Use Surya OCR
   		-	 `use_json`		    - Use JSON as AI input
   		-	 `use_markdown`	    - Use MARKDOWN as AI input
   		-	 `give_ai_raw_pdf`  - Allows you to give PDF directly to AI Model. Most models do not support this.
   		-	 `clean_output_dir` - Determine if files are deleted after use. Useful for debugging as raw AI ouput is also generated. NOTE: This does not delete the excel output because that is handled by an API.
   		-	 `model_version`	- LLM used.
		-    `directories`	    - Name of input and output directories for pipeline. 
		 
   - `section_fields.json`: Data fields to extract from PDF. Each new section represents a sheet in excel.
   - `custom_prompt.txt`: AI prompt
   - `ai_output_parser.py`: Parses output of AI Model into a format for pandas library. Modify if you expect to change the output of model. (Right now parser expects structured CSV output from model)  

6. **Run the pipeline**  
   Use `sbatch RunModel.sh` or run manually.

## 📁 Folder Structure

```
Pipeline_Process/
├── raw/                      # Input PDFs
├── excel_output/             # Output Excels
├── section_fields.json       # Defines extractable fields
├── custom_prompt.txt         # Prompt template
├── config.json               # Pipeline config
├── ai_output_parser.py       # AI output parser
├── pipeline.py               # Main script
├── RunModel.sh               # sbatch job script
└── requirements.txt          # Dependencies
```
