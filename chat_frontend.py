import streamlit as st
import json
import uuid
import os
from chat_backend import chatResponse

def save_uploaded_file(uploaded_file):
    # Create temporary directory if it doesn't exist
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    # Generate unique file name
    file_name = f"temp/{uuid.uuid4()}.{uploaded_file.name.split('.')[-1]}"
    
    # Save the file
    with open(file_name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_name

def main():
    st.title("Invoice Information Extractor")
    st.write("Upload an invoice image to extract information")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    print("This is uploaded ",uploaded_file)
    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        # Save the file and get the path
        file_path = save_uploaded_file(uploaded_file)
        
        try:
            # Get the response from backend
            response = chatResponse(file_path)
        
            
            # Parse the JSON response
            data = json.loads(response)
            formatted_json = json.dumps(data, indent=2, sort_keys=True)
            print(formatted_json)
            
            # Display company name
            st.subheader("Company Information")
            if data["response"]["company_name"]:
                company_name = data["response"]["company_name"]
                st.text_input("Company Name", value=company_name, disabled=True)
            else:
                st.text_input("Company Name", value=" ", disabled=True)
            
            # Display items
            st.subheader("Items List")
            items = data["response"]["items"]
            
            if not items:
                st.write("No items found in the document")
            else:
                # Create table-like structure using columns
                col1, col2 = st.columns([3, 1])
                col1.subheader("Item Name")
                col2.subheader("Price")
                i=0
                for item in items:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.text_input(
                            label="Item Name",
                            value=item["item_name"],
                            key=f"name_{item.get('item_name')} {i}",
                            disabled=True,
                            label_visibility='collapsed'
                        )
                    with col2:
                        st.text_input(
                            label="Price",
                            value=item["item_price"],
                            key=f"price_{item.get('item_price')} {i}",
                            disabled=True,
                            label_visibility='collapsed'
                        )
                        print(i)
                        i=i+1
                    

            # Display total amount
            total_amount = data["response"]["total_price"]
            st.subheader("Total Amount")
            st.text_input("Total Amount", value=total_amount, disabled=True)
            
            # Clean up temporary file
            os.remove(file_path)
            
        except Exception as e:
            st.error(f"Error processing image: {str(e)}")
            # Clean up temporary file even if there's an error
            if os.path.exists(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    main()