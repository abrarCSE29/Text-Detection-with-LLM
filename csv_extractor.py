import pandas as pd
import json
import os

# Load the CSV file
csv_file = "image_metadata.csv"  # replace with your actual file path
df = pd.read_csv(csv_file)

response_directory = "./dataset_detections"
os.makedirs(response_directory, exist_ok=True)

# Function to extract image number from the image path
def extract_image_number(image_path):
    # Extract the image number from the path (assuming it's in the format 'image_x.png')
    image_name = os.path.basename(image_path)
    image_number = int(image_name.split('_')[1].split('.')[0])  # Extracts number after 'image_'
    return image_number

# Function to safely parse the ground_truth column
def parse_ground_truth(ground_truth_str):
    try:
        # Parse the string into a JSON object
        return json.loads(ground_truth_str)
    except json.JSONDecodeError:
        print(f"Error decoding JSON for: {ground_truth_str}")
        return None

# Function to extract the relevant data from the ground_truth JSON
def extract_gt_info(ground_truth_json):
    if not ground_truth_json:
        return {}

    data = ground_truth_json
    
    # Extract 'gt_parse' -> 'menu' (cnt, nm, price)
    menu_items = []
    for item in data.get("gt_parse", {}).get("menu", []):
        if isinstance(item, dict):  # Ensure item is a dictionary
            menu_items.append({
                "cnt": item.get("cnt"),
                "nm": item.get("nm"),
                "price": item.get("price")
            })

    if len(menu_items) == 0:
        print("No menu items")
        gt_parse = data.get("gt_parse", {}).get("menu", {})
        menu_items.append({
            "cnt": gt_parse.get("cnt", ""),  # Get cnt from gt_parse
            "nm": gt_parse.get("nm", ""),    # Get nm from gt_parse
            "price": gt_parse.get("price", "")  # Get price from gt_parse
        })
        print(menu_items)
    # Extract total price
    total_price = data.get("gt_parse",{}).get("total", {}).get("total_price", "")
    
    return {
        "gt_parse": {
            "menu": menu_items
        },
        "total": {
            "total_price": total_price
        }
    }
i=1
# Loop through each row in the CSV and process the information
for index, row in df.iterrows():
    image_path = row['image_path']
    ground_truth_str = row['ground_truth']

    # Extract image number
    image_number = extract_image_number(image_path)
    
    # Parse the ground_truth string into a JSON object
    ground_truth_json = parse_ground_truth(ground_truth_str)

  
    
   
    
    
    if ground_truth_json:
        # Extract relevant ground truth information
        extracted_info = extract_gt_info(ground_truth_json)
        log_response_path = os.path.join(response_directory, f"{image_number}.json")
        # Save to a new JSON file with the image number as the filename
        with open(log_response_path, 'w') as json_file:
            json.dump(extracted_info, json_file, indent=2)

        # print(f"Processed image {image_number} and saved to {log_response_path}")
