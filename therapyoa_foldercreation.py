import os
import shutil
import therapyoa_pdfreader as pdf_reader


# Function to create a client folder
def create_client_folder(folder_path, name, assessment_file_path):
    client_folder = os.path.join(folder_path, name)

    # Check if the client folder already exists
    if os.path.exists(client_folder):
        print("Client folder already exists:", client_folder)
        return

    try:
        # Create the client folder
        os.mkdir(client_folder)

        # Create the subfolders inside the client folder
        subfolders = ['Onboarding', 'Service Notes', 'Disciplinary', 'Offboarding']
        for subfolder in subfolders:
            os.mkdir(os.path.join(client_folder, subfolder))

        print("Client folder created:", client_folder)

        # Move the assessment file to the Onboarding folder
        onboarding_folder = os.path.join(client_folder, 'Onboarding')
        assessment_file_name = os.path.basename(assessment_file_path)
        assessment_dest_path = os.path.join(onboarding_folder, assessment_file_name)
        os.rename(assessment_file_path, assessment_dest_path)
        print("Assessment file moved to Onboarding folder")

    except Exception as e:
        print("Error creating client folder:", str(e))
# Function to move files to a subfolder
def move_files_to_subfolder(file_path, folder_path, subfolder_name):
    if not os.path.isfile(file_path):
        print("Invalid file path:", file_path)
        return

    subfolder_path = os.path.join(folder_path, subfolder_name)
    if not os.path.exists(subfolder_path):
        os.mkdir(subfolder_path)

    try:
        file_name = os.path.basename(file_path)
        destination_path = os.path.join(subfolder_path, file_name)
        shutil.move(file_path, destination_path)
        print("File moved to subfolder:", file_name, "->", subfolder_name)

    except Exception as e:
        print("Error moving file to subfolder:", str(e))

if __name__ == "__main__":
    assessment_file_path = ""
    root_directory = r"D:\THC Organizational Assistant\TherapyOA"
    extracted_info = pdf_reader.extract_client_info(assessment_file_path)
    name = extracted_info['Name']
    create_client_folder(root_directory, name)

