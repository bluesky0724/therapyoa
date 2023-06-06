import os
from tkinter import messagebox
import shutil


def sort_notes():
    # Specify the path to the "Generated Notes" folder
    generated_notes_folder = os.path.join(root_directory, "Generated Notes")

    # Check if the "Generated Notes" folder exists
    if not os.path.exists(generated_notes_folder):
        messagebox.showinfo("Error", "The 'Generated Notes' folder does not exist.")
        return

    # Get a list of all files in the "Generated Notes" folder
    file_list = os.listdir(generated_notes_folder)

    # Iterate over each file in the folder
    for file_name in file_list:
        # Extract the first three words from the file name
        elements = file_name.split()
        client_identifier = " ".join(elements[:3])

        # Search for matching client folders
        matching_folders = search_clients(client_identifier)

        if matching_folders:
            # Move the file to the first matching folder
            folder_path = matching_folders[0]
            source_path = os.path.join(generated_notes_folder, file_name)
            destination_path = os.path.join(folder_path, file_name)
            shutil.move(source_path, destination_path)
            messagebox.showinfo("Success", f"File '{file_name}' moved to folder: {folder_path}")
        else:
            messagebox.showinfo("Error", f"No matching client folder found for file: {file_name}")