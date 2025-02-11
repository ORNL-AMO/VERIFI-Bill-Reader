import ollama
import os
import pandas as pd
import re  

# Load the installed model
model_name = "deepseek-r1:7b"

# Get the base directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the absolute path to the uploads folder
uploads_dir = os.path.join(script_dir, "uploads")

# Ensure the uploads directory exists
if not os.path.exists(uploads_dir):
    print(f"Error: The uploads directory does not exist at {uploads_dir}")
    exit()

# Find all markdown files (.md and .markdown)
markdown_files = [f for f in os.listdir(uploads_dir) if f.lower().endswith((".md", ".markdown"))]

if not markdown_files:
    print("Error: No Markdown files found in uploads directory.")
    exit()

# Select the first available markdown file
markdown_file = os.path.join(uploads_dir, markdown_files[0])
print(f"Processing file: {markdown_file}")

# Read the Markdown content
with open(markdown_file, "r", encoding="utf-8") as file:
    markdown_content = file.read()

# Define fields to extract
fields = [
    "Address", "Zip Code", "State"
]

# Initialize extracted data
extracted_data = {field: "BLANK" for field in fields}  # Default to BLANK
full_ai_responses = {}  # Store full AI reasoning + answers

# Function to clean AI response and extract final answer
def extract_final_answer(ai_response):
    """ Extracts final answer from AI response, removing <think> tags and returning only the extracted value. """
    raw_response = ai_response.strip()
    
    # Debug: Store raw response for logging
    full_ai_responses[field] = raw_response
    
    # Remove everything inside <think>...</think>
    cleaned_text = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL).strip()
    
    # If AI gives an empty response, return "BLANK"
    return cleaned_text if cleaned_text else "BLANK"

# Loop through fields and extract data
for field in fields:
    prompt = (
        f"Extract the {field} from the following Markdown file. "
        f"Only return the extracted value with no explanation, comments, or extra words. "
        f"If the {field} is not found, return exactly: BLANK.\n\n"
        f"{markdown_content}"
    )
    
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    
    extracted_value = extract_final_answer(response["message"]["content"])  # Process AI response
    extracted_data[field] = extracted_value  # Store final value

# Save extracted data to an Excel file
output_excel_path = os.path.join(uploads_dir, "extracted_data.xlsx")
df = pd.DataFrame([extracted_data])  # Convert dict to DataFrame
df.to_excel(output_excel_path, index=False)

# Save AI’s full responses for debugging
debug_log_path = os.path.join(uploads_dir, "ai_responses_log.txt")
with open(debug_log_path, "w", encoding="utf-8") as log_file:
    for field, response in full_ai_responses.items():
        log_file.write(f"--- {field} ---\n{response}\n\n")

print(f"Extracted data saved to: {output_excel_path}")
print(f"AI responses saved to: {debug_log_path}")
