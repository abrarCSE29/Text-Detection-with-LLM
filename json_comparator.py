import json
import os

# Define directories
responses_dir = "Responses"
detections_dir = "dataset_detections"
log_dir = "differences_log"

# Ensure log directory exists
os.makedirs(log_dir, exist_ok=True)

def load_json(file_path):
    """Load JSON data from a file while handling null characters."""
    if not os.path.exists(file_path):
        return None  # Return None if file is missing
    with open(file_path, 'rb') as file:  # Open in binary mode
        raw_data = file.read().replace(b'\x00', b'')  # Remove null bytes
        try:
            return json.loads(raw_data.decode("utf-8", errors="ignore"))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_path}: {e}")
            return None

def compare_json(json1, json2, path=""):
    """Compare two JSON objects and log differences."""
    differences = []
    
    # Check for keys in json1 not in json2
    for key in json1:
        new_path = f"{path}.{key}" if path else key
        if key not in json2:
            differences.append(f"Key missing in second JSON: {new_path}")
        else:
            if isinstance(json1[key], dict) and isinstance(json2[key], dict):
                differences.extend(compare_json(json1[key], json2[key], new_path))
            elif isinstance(json1[key], list) and isinstance(json2[key], list):
                if len(json1[key]) != len(json2[key]):
                    differences.append(f"List length mismatch at {new_path}")
                else:
                    for index, (item1, item2) in enumerate(zip(json1[key], json2[key])):
                        differences.extend(compare_json(item1, item2, f"{new_path}[{index}]"))
            else:
                if json1[key] != json2[key]:
                    differences.append(f"Value mismatch at {new_path}: (Gemini Response) {json1[key]} != (Dataset Detection) {json2[key]}")

    # Check for keys in json2 not in json1
    for key in json2:
        new_path = f"{path}.{key}" if path else key
        if key not in json1:
            differences.append(f"Key missing in first JSON: {new_path}")

    return differences

def log_differences(differences, log_file):
    """Log differences to a text file."""
    with open(log_file, "w", encoding="utf-8") as file:
        for diff in differences:
            file.write(diff + "\n")

# Iterate through JSON files in Responses/
for file_name in os.listdir(responses_dir):
    if file_name.endswith(".json"):
        file_number = os.path.splitext(file_name)[0]  # Extract number from filename
        json_file_1 = os.path.join(responses_dir, file_name)
        json_file_2 = os.path.join(detections_dir, file_name)  # Matching file in dataset_detections

        # Load both JSON files
        json1 = load_json(json_file_1)
        json2 = load_json(json_file_2)

        # Skip if any file is missing
        if json1 is None or json2 is None:
            print(f"Skipping {file_name} (missing file)")
            continue

        # Compare JSON data
        differences = compare_json(json1, json2)

        # Log differences if found
        if differences:
            log_file_path = os.path.join(log_dir, f"{file_number}.txt")
            log_differences(differences, log_file_path)
            print(f"Differences found! Logged in '{log_file_path}'.")
        else:
            print(f"No differences in {file_name}.")
