import zipfile
import os

folder_path = r"C:\Users\odebi\Desktop\download audio"

for file in os.listdir(folder_path):
    if file.endswith(".zip"):
        file_path = os.path.join(folder_path, file)
        extract_path = os.path.join(folder_path, file.replace(".zip", ""))

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)