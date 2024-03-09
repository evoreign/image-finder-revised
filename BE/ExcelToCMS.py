import pandas as pd
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import pytz

client = MongoClient("mongodb+srv://kopi:kopi@cluster0.1lc1x8s.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["test"]
collection = db["models"]

# Create a unique index on the 'ModelName' field
collection.create_index("ModelName", unique=True)

while True:
    root_path = input("Enter the root path: ")
    list_of_models = os.listdir(root_path)
    print(list_of_models)
    confirmations = input("Are these the models you want to use? (y/n): ")
    if confirmations == "y":
        print("Great! Let's move on.")
        for model in list_of_models:
            print(f"Model: {model}")
            model_path = os.path.join(root_path, model)
            files = os.listdir(model_path)
            for file in files:
                print(f"File: {file}")
                file_path = os.path.join(model_path, file)
                cleaned_file_name = file.split(".")[0]
                df = pd.read_excel(file_path, sheet_name=cleaned_file_name)
                print("Available columns",df.columns)

                # Create separate dataframes based on whether columns '250', '500', '1000', '2000', '4000', '5000' are filled
                ps_type = {}
                for col in ['250', '500', '1000', '2000', '4000', '5000']:
                    if col in df.columns and 'Image' in df.columns:
                        df_temp = df[df[col].notna()]
                        df_temp = df_temp[df_temp['Image'].notna()]
                        # Convert 'Image' column to integers
                        df_temp['Image'] = df_temp['Image'].astype(int)
                        # Only take certain columns
                        df_temp = df_temp[['Image', 'Tab', 'Section']]
                        # Convert dataframe to dictionary
                        ps_type_dict = df_temp.set_index('Image').to_dict('index')
                        # Convert keys to strings
                        ps_type[col] = {str(key): value for key, value in ps_type_dict.items()}
                        print(f"ps_type[{col}]: {ps_type[col]}")  # print the ps_type for debugging
                    else:
                        print(f"Column {col} not found in DataFrame columns or 'Image' column is missing.")  # print a message if the column is not found

                # Create document for MongoDB
                document = {
                    'ModelName': model,
                    'ImageUrl': 'blank.png',
                    'PsType': ps_type,
                    'createdAt': datetime.now(pytz.timezone('Asia/Jakarta')),  # current date and time in Jakarta time zone
                    'updatedAt': datetime.now(pytz.timezone('Asia/Jakarta')),  # current date and time in Jakarta time zone
                    '__v': 0
                }

                print(f"Document: {document}")  # print the document for debugging

                try:
                    # Insert document into MongoDB
                    collection.insert_one(document)
                except DuplicateKeyError:
                    print(f"A document with ModelName {model} already exists.")
    else:
        continue