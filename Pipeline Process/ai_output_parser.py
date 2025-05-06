# Parse the CSV-like output from AI

import re

def parse_ai_response(cleaned_response, fields):
    extracted_records = []

    lines = cleaned_response.splitlines()
    for line in lines:
        values = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)

        if not any(v.strip() for v in values):
            continue  # skip empty rows

        # Pad or trim to match expected length
        if len(values) < len(fields):
            values += [''] * (len(fields) - len(values))
        elif len(values) > len(fields):
            values = values[:len(fields)]

        record = {field: value.strip().strip('"') for field, value in zip(fields, values)}
        extracted_records.append(record)

    return extracted_records
