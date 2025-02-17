import os
import google.generativeai as genai
from google.ai.generativelanguage_v1beta.types import content
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Upload the image to the model
def upload_image(file_path):
    sample_file = genai.upload_file(path=file_path, display_name="Sample drawing")
    print(sample_file)
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    return sample_file
     
# Create the model
generation_config = {
  "temperature": 0,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_schema": content.Schema(
    type = content.Type.OBJECT,
    properties = {
      "response": content.Schema(
        type = content.Type.OBJECT,
        properties = {
          "company_name": content.Schema(
            type = content.Type.STRING,
          ),
          "items": content.Schema(
            type = content.Type.ARRAY,
            items = content.Schema(
              type = content.Type.OBJECT,
              properties = {
                "item_name": content.Schema(
                  type = content.Type.STRING,
                ),
                "item_price": content.Schema(
                  type = content.Type.STRING,
                ),
              },
            ),
          ),
          "total_price": content.Schema(
            type = content.Type.STRING,
          ),
        },
      ),
    },
  ),
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
  system_instruction="use ocr on the receipt image and return necessary info in structured JSON format",
)

def chatResponse(file_path):
  
    response = model.generate_content(
      ["This is the image",upload_image(file_path)]
    )
    
    i=0
    directory = "./Responses/"

    os.makedirs(directory,exist_ok=True)

    
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # Format: YYYY-MM-DD_HH-MM-SS

    log_response = os.path.join(directory, f"{timestamp}_reponse_image_{i}.txt")

    with open(log_response, "w") as file:
      file.write(response.text)
    
    return response.text
    

