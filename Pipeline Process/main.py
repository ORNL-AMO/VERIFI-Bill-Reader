import os
os.environ["OLLAMA_MODELS"] = "./ollama/models"
import ollama
import pandas as pd
import shutil
import re
import json

#############################################################################################################
#############################################################################################################
#############################################################################################################

# Load user config file

with open('config.json', 'r') as f:
    config = json.load(f)

# Load config variables

USE_MARKER_OCR = config.get("use_marker_ocr", True)
USE_MARKDOWN = config.get("use_markdown", True)
USE_JSON = config.get("use_json", True)
GIVE_AI_RAW_PDF = config.get("give_ai_raw_pdf", True)
DELETE_FILES = config.get("clean_output_dir", True)
MODEL_VERSION = config.get("model_version", "llama3.2-vision:90b")

DIR = config["directories"]["raw_pdf"]
OUTPUT_DIR = config["directories"]["output"]
EXCEL_DIR = config["directories"]["excel_output"]

# Create directories if they do not exist

os.makedirs(DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)

#############################################################################################################
#############################################################################################################
#############################################################################################################

# Count number of PDF in raw folder for Surya OCR
def count_pdf_files():
    pdf_count = 0
    last_filename = None
    try:
        for filename in os.listdir(DIR):
            if filename.lower().endswith('.pdf'):
                pdf_count += 1
                last_filename = filename
                pdf_name_base = os.path.splitext(filename)[0]
        return pdf_count, last_filename, pdf_name_base
    except Exception as e:
        print(f"Error accessing directory: {e}")
        return 0, None
num_pdfs, last_filename, pdf_name_base = count_pdf_files()

print(f"Found {num_pdfs} PDF(s) in {DIR}")

# This function makes sure that the output files are not put into folders 
# (for Surya OCR or OCR that places each set of json+markdown in a folder)
def flatten_marker_output(output_dir):
    subdirs = [os.path.join(output_dir, d) for d in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, d))]

    if not subdirs:
        print("No subfolders found in output directory.")
        return

    for subdir in subdirs:
        for filename in os.listdir(subdir):
            src = os.path.join(subdir, filename)
            dst = os.path.join(output_dir, filename)
            shutil.move(src, dst)
        os.rmdir(subdir)
        print(f"Extracted data and removed subfolder: {subdir}")

#############################################################################################################
#############################################################################################################
#############################################################################################################

# Check if Surya OCR is enabled and run it if necessary

if USE_MARKER_OCR:
    # Run Surya OCR to generate markdown and json
    if num_pdfs >= 1:
        os.system(f"marker_single --output_dir {OUTPUT_DIR} {DIR}{last_filename}") 
        flatten_marker_output(OUTPUT_DIR)
    else:
        raise ValueError("No PDF files found. Exiting.")
else:
    markdown_content = ""
    json_content = {}

# Check if the user intends to use markdown files and if so, read the content

if USE_MARKDOWN:
    # Process Markdown file
    markdown_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith(('.md', '.markdown'))]
    if not markdown_files:
        raise ValueError("No Markdown files found in output directory.")

    # Try to find matching markdown file
    markdown_file = None
    for ext in ['.md', '.markdown']:
        candidate = f"{pdf_name_base}{ext}"
        if candidate in markdown_files:
            markdown_file = os.path.join(OUTPUT_DIR, candidate)
            break
    if not markdown_file:
        markdown_file = os.path.join(OUTPUT_DIR, markdown_files[0])    
    
    print(f"Processing Markdown file: {markdown_file}")

    with open(markdown_file, 'r', encoding='utf-8') as file:
        markdown_content = file.read()
else:
    markdown_content = ""

# Check if the user intends to use json files, and if so, read the content

if USE_JSON:
    # Process JSON file
    json_files = [f for f in os.listdir(OUTPUT_DIR) if f.lower().endswith('.json')]
    if not json_files:
        raise ValueError("No JSON files found in output directory.")

    json_name = f"{pdf_name_base}_meta.json"
    if json_name in json_files:
        json_file = os.path.join(OUTPUT_DIR, json_name)
    else:
        json_file = os.path.join(OUTPUT_DIR, json_files[0])
    
    print(f"Processing Json file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as file:
        json_content = json.load(file)
else:
    json_content = {}

# Raw PDF
pdf_file = os.path.join(DIR, last_filename)
raw_pdf_content = pdf_file if GIVE_AI_RAW_PDF else ""

#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################

# Define all sections and their corresponding fields
with open('section_fields.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)

# Hardcoded sections below (Uncomment if json for section setup is not being used)
'''
    sections = {
    "Facilities": [
        "Facility Name", "Address", "Country", "State", "City", "Zip",
        "NAICS Code 2 digit", "NAICS Code 3 digit", "Contact Name",
        "Contact Phone", "Contact Email"
    ],
    "Meter-Utilities": [
        "Facility Name", "Meter Number", "Source", "Scope", "Meter Name (Display)",
        "Meter Group", "Calendarize Data?", "Phase or Vehicle", "Fuel or Emission",
        "Collection Unit", "Energy Unit", "Distance Unit", "Estimation Method",
        "Heat Capacity or Fuel Efficiency", "Include In Energy", "Site To Source",
        "Agreement Type", "Retain RECS", "Account Number", "Utility Supplier",
        "Notes", "Building/Location"
    ],
    "Electricity": [
        "Meter Number", "Read Date", "Total Consumption", "Total Real Demand",
        "Total Billed Demand", "Total Cost", "Non-energy Charge", "Block 1 Consumption",
        "Block 2 Consumption Charge", "Block 3 Consumption", "Other Consumption",
        "Other Consumption Charge", "On Peak Amount", "On Peak Charge", "Off Peak Amount",
        "Off Peak Charge", "Transmission & Delivery Charge", "Power Factor Charge",
        "Local Sales Tax", "State Sales Tax", "Late Payment", "Other Charge"
    ],
    "Stationary Fuel - Other Energy": [
        "Meter Number", "Read Date", "Total Consumption", "Total Cost",
        "Higher Heating Value", "Commodity Charge", "Delivery Charge",
        "Other Charge", "Demand Usage", "Demand Charge", "Local Sales Tax",
        "State Sales Tax", "Late Payment"
    ],
    "Mobile Fuel": [
        "Meter Number", "Read Date", "Total Consumption or Total Distance",
        "Fuel Efficiency", "Total Cost", "Other Charge"
    ],
    "Water": [
        "Meter Number", "Read Date", "Total Consumption", "Total Cost",
        "Commodity Charge", "Delivery Charge", "Other Charge", "Demand Usage",
        "Demand Charge", "Local Sales Tax", "State Sales Tax", "Late Payment"
    ],
    "Other Utility - Emission": [
        "Meter Number", "Read Date", "Total Consumption", "Total Cost", "Other Charge"
    ]
}
'''

# Helper function to clean AI response (If AI Model has <think> tags or reasoning component)
def extract_final_answer(ai_response):
    raw_response = ai_response.strip()
    cleaned_text = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip() # Change regex to match the output of AI you want to clean
    return cleaned_text if cleaned_text else ""

# Function to extract multiple records for each section
def extract_section_data(section_name, fields, markdown_content, json_content, raw_pdf_content):
    extracted_records = []

    # Load prompt from file
    with open('custom_prompt.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    # Fill in keywords with values
    prompt = prompt_template.format(
        section_name=section_name,
        fields=', '.join(fields),
        markdown_content=markdown_content,
        json_content=json.dumps(json_content, indent=2),
        raw_pdf_content=raw_pdf_content,
        field_count=len(fields)
    )

    # Hardcoded prompt below (Uncomment if json for custom prompt is not being used)
    ''' 
    prompt = (
        f"Extract all records for '{section_name}' from the following content. "
        f"Return as a CSV format where each row represents a record. If a field is missing, return a single space.\n\n"
        f"Do not return no value. Always return a csv format. If you can't find anything just return a single space for that item."
        f"Fields: {', '.join(fields)}\n\n"
        f"From the fields above extract the records in csv format. You will be given up to three versions of the same content below. They should each be identical so just use the JSON/Raw PDf for making sure result is correct.\n\n"
        f"## Markdown Content:\n{markdown_content}\n\n"
        f"## JSON Content:\n{json.dumps(json_content, indent=2)}\n\n"
        f"## Raw PDF Content:\n{raw_pdf_content}\n\n"
        f"ONLY return the CSV data. No extra explanations or text.\n\n"
        f"Do not repeat the section name or field in your response. Create a new line of csv for each meter or item if there are multiple answers."
    )
    '''
    
    # Use the running Ollama server to get the AI response to the prompt
    # The model must be running and available to get a response
    response = ollama.chat(model=MODEL_VERSION, messages=[{"role": "user", "content": prompt}])
     
    # Output the raw AI response to a text file
    with open(os.path.join(OUTPUT_DIR, f"raw_response_{section_name}.txt"), "w", encoding="utf-8") as f:
        f.write(response["message"]["content"])
    
    cleaned_response = extract_final_answer(response["message"]["content"])

    # If the response is empty create a blank dataframe for the section (This should not happen unless model returns bad result or crashes)
    if cleaned_response == "BLANK" or not cleaned_response:
        print(f"No data found for section: {section_name}. Creating a blank sheet.")
        return pd.DataFrame(columns=fields)  # Return an empty DataFrame with just column names

  # Parse the CSV-like output from AI
    lines = cleaned_response.splitlines()
    for line in lines:
        # Split on commas not inside quotes
        values = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)
        if len(values) == len(fields):
            record = {field: value.strip().strip('"') for field, value in zip(fields, values)}
            extracted_records.append(record)
    return extracted_records
    
# Main function to process Markdown and export to Excel
def process_markdown_to_excel(markdown_content, json_content, raw_pdf_content, output_path):
    all_data = {}

    # Extract data for each section
    for section_name, fields in sections.items():
        records = extract_section_data(section_name, fields, markdown_content, json_content, raw_pdf_content)
        all_data[section_name] = pd.DataFrame(records or [], columns=fields)

    # Write to an Excel workbook with multiple sheets
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for section_name, df in all_data.items():
            df.to_excel(writer, sheet_name=section_name, index=False)

    print(f"Data successfully extracted and saved to: {output_path}")

# Path for Excel
output_excel_path = os.path.join(EXCEL_DIR, f"{pdf_name_base}.xlsx")

# Run the AI Model on the content created from OCR
process_markdown_to_excel(markdown_content, json_content, raw_pdf_content, output_excel_path)

# Removes all files from the output folder
if DELETE_FILES:
    # Delete files in output folder
    for f in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, f)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Delete PDF processed
    for f in os.listdir(DIR):
        if f.startswith(pdf_name_base) and f.lower().endswith(".pdf"):
            os.remove(os.path.join(DIR, f))
else:
    print("Warning: Files were not deleted because setting was disabled in config file.")
