from docx import Document
import therapyoa_foldercreation as folder_creation
import therapyoa_pdfreader as pdf_reader
import therapyoa_nomenclature as nomenclature
import therapyoa_sortnotes as sortnotes
import therapyoa_database as database
import webbrowser
from tkinter import Button, ttk, Label, Entry, StringVar, filedialog, Listbox, OptionMenu, Text, END, MULTIPLE, messagebox
import datetime
import openai
import shutil
import zipfile
import os
import tkinter as tk
from tkinter import messagebox
import sqlite3

# declaring globals
openai.api_key = "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"
intake_file_path = ""
assessment_file_path = ""
root_directory = r"D:\THC Organizational Assistant\TherapyOA\Clients"
absolute_path = os.path.dirname(__file__)
selected_client_info = ""
selected_files = []  # Global variable to store the selected files


def create_folders():
    folders = ["TherapyOA", "TherapyOA/Clients",
               "TherapyOA/App Resources", "TherapyOA/Unsorted Notes"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def initialize_app():
    # Check if the baseline folders already exist
    if os.path.exists("TherapyOA"):
        print("Baseline folders already exist.")
    else:
        create_folders()
        print("Baseline folders created successfully.")


# Check if the baseline setup is already done
def is_baseline_setup_done():
    # Check if the necessary folders exist
    if not os.path.exists(root_directory):
        return False
    if not os.path.exists(clients_directory):
        return False
    if not os.path.exists(resources_directory):
        return False

    return count > 0


def set_api_key():
    # Retrieve the API key from the user
    api_key = api_key_entry.get()

    # Set the API key in the openai module
    openai.api_key = api_key

    # Show a message to confirm that the API key has been set
    messagebox.showinfo("API Key", "API key has been set.")


def open_intake_file_explorer():
    global intake_file_path
    intake_file_path = filedialog.askopenfilename(title="Select Intake File")
    print("Selected intake file:", intake_file_path)


def open_assessment_file_explorer():
    global assessment_file_path, extracted_info
    assessment_file_path = filedialog.askopenfilename(
        title="Select Assessment File")
    print("Selected assessment file:", assessment_file_path)
    extracted_info = pdf_reader.extract_client_info(assessment_file_path)


def client_exists(name, dob, ahcccs_id):
    conn = sqlite3.connect('client_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM clients WHERE name = ? AND date_of_birth = ? AND ahcccs_id = ?",
                   (name, dob, ahcccs_id))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


def add_client():
    global intake_file_path, assessment_file_path, root_directory
    # check if all input fields are filled
    if not intake_file_path or not assessment_file_path or not root_directory:
        messagebox.showinfo("Missing Information",
                            "Please provide all the necessary file paths.")
        return

    # Extract client information from the assessment PDF
    assessment_info = pdf_reader.extract_client_info(assessment_file_path)
    if not assessment_info:
        messagebox.showinfo(
            "PDF Failure", "Failed to extract client information from the assessment PDF.")
        return

    name = assessment_info['Name']
    dob = assessment_info['DOB']
    ahcccs_id = ahcccs_id_entry.get()
    # Check if the client already exists in the database
    if client_exists(name, dob, ahcccs_id):
        messagebox.showinfo("Duplicate Client",
                            "Client already exists in the database.")
        return
    # Create the client folder and subfolders
    client_folder_path = os.path.join(root_directory, name + " " + ahcccs_id)
    os.mkdir(client_folder_path)  # Create the client folder

    subfolders = ['Onboarding', 'Offboarding', 'Disciplinary', 'Service Notes']
    for subfolder in subfolders:
        subfolder_path = os.path.join(client_folder_path, subfolder)
        os.mkdir(subfolder_path)

    # Move intake and assessment files to the Onboarding folder
    folder_creation.move_files_to_subfolder(
        intake_file_path, client_folder_path, 'Onboarding')
    folder_creation.move_files_to_subfolder(
        assessment_file_path, client_folder_path, 'Onboarding')
    # Add client information to the database
    conn = sqlite3.connect('client_database.db')
    cursor = conn.cursor()

    # Execute an SQL INSERT statement
    cursor.execute("INSERT INTO clients (name, date_of_birth, ahcccs_id) VALUES (?, ?, ?)",
                   (name, dob, ahcccs_id))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def add_client_button():
    global intake_file_path, assessment_file_path, root_directory

    if not intake_file_path or not assessment_file_path or not root_directory:
        messagebox.showinfo(
            "Missing Info", "Please provide all the necessary file paths and root directory.")
        return

    # Update the command to directly call the add_client function
    add_client(intake_file_path, assessment_file_path, root_directory)


def fetch_client_list():
    conn = sqlite3.connect('client_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM clients")
    client_list = [row[0] for row in cursor.fetchall()]
    conn.close()
    return client_list

# Function to search for clients in the folders based on criteria


def search_clients(name):
    matching_folders = []
    root_directory

    for folder_name in os.listdir(root_directory):
        folder_path = os.path.join(root_directory, folder_name)

        if os.path.isdir(folder_path):
            # Extract client name from the folder name
            client_name = folder_name

            if name == client_name:
                matching_folders.append(folder_path)

    return matching_folders


def open_folder(event):
    # Get the clicked item
    item_id = treeview.focus()

    # Get the folder path associated with the clicked item
    folder_path = treeview.item(item_id, 'text')

    # Open the folder in the default file explorer
    webbrowser.open(folder_path)


def search_button_clicked():
    # Get the value entered in the search field
    name = name_entry.get()
    matching_folders = search_clients(name)

    # Remove existing result labels
    for label in search_client_frame.winfo_children():
        if isinstance(label, ttk.Label):
            label.pack_forget()
        # Clear the treeview
        treeview.delete(*treeview.get_children())

    for folder_path in matching_folders:
        # Insert the folder path as an item in the treeview
        treeview.insert("", "end", text=folder_path)


def fetch_all_clients():
    # Connect to the database and create a cursor object
    conn = sqlite3.connect('client_database.db')
    cursor = conn.cursor()

    # Execute an SQL query to fetch all client names from the database
    cursor.execute("SELECT name FROM clients")

    # Fetch all the rows as a list of tuples
    rows = cursor.fetchall()

    # Close the connection
    conn.close()

    # Extract client names from the rows
    client_names = [row[0] for row in rows]

    return client_names


def populate_client_listbox():
    # Clear the listbox
    listbox.delete(0, tk.END)

    # Fetch the client list from the database
    client_list = fetch_client_list()
    print("Fetched client list:", client_list)
    # Populate the listbox
    for client in client_list:
        listbox.insert(tk.END, client)

    # Preselect the first item if the list is not empty
    if client_list:
        listbox.selection_set(0)


def retrieve_client_information(client_name):
    conn = sqlite3.connect('client_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE name = ?", (client_name,))
    client_information = cursor.fetchone()
    conn.close()
    return client_information


def generate_notes():
    # Check if an item is selected in the listbox
    if not listbox.curselection():
        messagebox.showinfo("Error", "No client selected.")
        return

    # Retrieve the selected client name from the listbox
    selected_clients = [listbox.get(idx) for idx in listbox.curselection()]

    # Get other information from the GUI
    date_of_service = date_of_service_entry.get()
    time = time_entry.get()
    note_type = note_type_var.get()
    note_details = note_details_entry.get("1.0", "end")

    # Generate DAP notes for each selected client
    for client in selected_clients:
        # Retrieve client information from the database
        client_information = retrieve_client_information(client)

        # Construct the prompt for the model with all the information
        prompt = f"Generate a DAP format note with the client's name (Name: {client}), DOB ({client_information[2]}), and AHCCCS ID ({client_information[3]}) at the top, with the Date of service ({date_of_service}), time of service ({time}), and Service Code ({note_type}) underneath. Underneath that, generate a paragraph for Data, Assessment, and Plan sections. For the Data section, use the following information: {note_details}. For the Assessment section, base the assessment on the data provided and generate what makes sense. For the Plan section, just copy the following: Plan: The plan for {client} is to continue supporting them in their recovery journey with consistent sessions to help them stick to their goals during and after they leave our tenure. End it with this: Provider Signature:________________________________."
        # Generate DAP notes using ChatGPT (text-davinci-003 model)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=500
        )

        # Get the generated DAP notes from the response
        generated_notes = response.choices[0].text.strip()

        # Create a document and add the generated notes
        document = Document()
        document.add_paragraph(generated_notes)
        # Create the "Generated Notes" folder in the root directory
        generated_notes_folder = os.path.join(root_directory, "Unsorted Notes")
        os.makedirs(generated_notes_folder, exist_ok=True)

        # Save the document as a .docx file in the "Generated Notes" folder
        file_name = f"{client}" + " " + \
            f"{client_information[3]}" + " " + \
            f"{note_type}" + " " + f"{date_of_service}.docx"
        file_path = os.path.join(generated_notes_folder, file_name)
        document.save(file_path)

    # Display a success message
    messagebox.showinfo(
        "Notes Generated", "DAP notes generated and saved in Unsorted Notes folder.")


def on_client_selection(event):
    global selected_client_info
    selected_index = discharge_listbox.curselection()
    if selected_index:
        selected_client = discharge_listbox.get(selected_index[0])
        client_information = retrieve_client_information(selected_client)
        selected_client_info = client_information


def sort_notes():
    # Specify the path to the "Unsorted Notes" folder
    unsorted_notes_folder = os.path.join(root_directory, "Unsorted Notes")

    # Check if the "Unsorted Notes" folder exists
    if not os.path.exists(unsorted_notes_folder):
        messagebox.showinfo(
            "Notes Sorting", "The 'Unsorted Notes' folder does not exist.")
        return

    # Get a list of all files in the "Unsorted Notes" folder
    file_list = os.listdir(unsorted_notes_folder)

    # Create a list to store the names of files that could not be sorted
    unsorted_files = []

    # Iterate over each file in the folder
    for file_name in file_list:
        # Extract the first three words from the file name
        elements = file_name.split()
        client_identifier = " ".join(elements[:3])

        # Search for matching client folders
        matching_folders = search_clients(client_identifier)

        if matching_folders:
            # Move the file to the "Service Notes" folder of the first matching client
            client_folder_path = os.path.join(
                matching_folders[0], "Service Notes")
            # Create the "Service Notes" folder if it doesn't exist
            os.makedirs(client_folder_path, exist_ok=True)
            source_path = os.path.join(unsorted_notes_folder, file_name)
            destination_path = os.path.join(client_folder_path, file_name)
            shutil.move(source_path, destination_path)
        else:
            unsorted_files.append(file_name)

    # Display a notification about the sorting status
    if not file_list:
        messagebox.showinfo(
            "Notes Sorting", "The 'Unsorted Notes' folder is empty.")
    elif not unsorted_files:
        messagebox.showinfo(
            "Notes Sorting", "All files have been successfully sorted.")
    else:
        messagebox.showinfo(
            "Notes Sorting", "Some files could not be sorted: " + ", ".join(unsorted_files))


def discharge_clients_button_clicked():
    # Check if any clients are selected
    if not discharge_listbox.curselection():
        messagebox.showinfo("Error", "No clients selected.")
        return

    # Retrieve the selected clients from the listbox
    selected_clients = [discharge_listbox.get(
        idx) for idx in discharge_listbox.curselection()]

    # Show a confirmation dialog
    confirmation_message = "Are you sure you want to discharge the following clients?\n\n" + \
        "\n".join(selected_clients)
    confirmed = messagebox.askyesno("Confirm Discharge", confirmation_message)

    if confirmed:
        # Iterate over the selected clients
        for client in selected_clients:
            # Retrieve client information from the database
            client_information = retrieve_client_information(client)

            # Remove the client from the database
            remove_client_from_database(client)

            # Zip the client folder
            zip_client_folder(client_information)

        # Update the discharge listbox
        populate_discharge_listbox()

        # Show a success message
        messagebox.showinfo(
            "Discharge Clients", "Selected clients have been discharged and their folders have been archived and deleted.")


def remove_client_from_database(client_name):
    conn = sqlite3.connect('client_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE name = ?", (client_name,))
    conn.commit()
    conn.close()


def zip_client_folder(client_information):
    client_name = client_information[1]
    ahcccs = client_information[3]
    client_folder_path = os.path.join(
        root_directory, f"{client_name} {ahcccs}")
    zip_file_name = f"{client_name}_{ahcccs}.zip"
    zip_file_path = os.path.join(root_directory, zip_file_name)

    with zipfile.ZipFile(zip_file_path, "w") as zip_file:
        for folder_name, subfolders, file_names in os.walk(client_folder_path):
            for file_name in file_names:
                file_path = os.path.join(folder_name, file_name)
                arc_name = os.path.relpath(file_path, client_folder_path)
                zip_file.write(file_path, arc_name)

    # Delete the client folder after zipping
    shutil.rmtree(client_folder_path)


def populate_discharge_listbox():
    # Clear the discharge listbox
    discharge_listbox.delete(0, tk.END)

    # Fetch the client list from the database
    client_list = fetch_client_list()

    # Print the fetched client list for debugging
    print("Fetched client list:", client_list)

    # Populate the discharge listbox
    for client in client_list:
        discharge_listbox.insert(tk.END, client)

    # Preselect the first item if the list is not empty
    if client_list:
        discharge_listbox.selection_set(0)


# Set the path to your custom icon file (should be in .ico format)
icon_path = os.getcwd() + "\\TherapyOA_icon.ico"

# Create the main window
root = tk.Tk()


root.title("TherapyOA")

# Set the icon for the window
root.iconbitmap(icon_path)
# Create a notebook widget
tab_control = ttk.Notebook(root)

# Add the "Add Client" tab
add_client_frame = ttk.Frame(tab_control)
tab_control.add(add_client_frame, text="Add Client")
tab_control.pack(expand=True, fill='both')

# Create the content for the "Add Client" tab
intake_label = ttk.Label(add_client_frame, text="Client Intake:")
intake_label.pack(pady=10)

intake_button = ttk.Button(
    add_client_frame, text="Browse", command=open_intake_file_explorer)
intake_button.pack()


assessment_label = ttk.Label(add_client_frame, text="Therapist Assessment:")
assessment_label.pack(pady=10)

assessment_button = ttk.Button(
    add_client_frame, text="Browse", command=open_assessment_file_explorer)
assessment_button.pack()

ahcccs_id_label = ttk.Label(add_client_frame, text="AHCCCS ID:")
ahcccs_id_label.pack(pady=10)

ahcccs_id_entry = ttk.Entry(add_client_frame, width=20)
ahcccs_id_entry.pack()

add_button = ttk.Button(
    add_client_frame, text="Add Client", command=add_client)
add_button.pack(pady=10)

# Add the "Client Search" tab
search_client_frame = ttk.Frame(tab_control)
tab_control.add(search_client_frame, text="Client Search")

# Create the content for the "Client Search" tab
name_label = ttk.Label(search_client_frame, text="Name:")
name_label.pack(pady=10)

name_entry = ttk.Entry(search_client_frame, width=20)
name_entry.pack()

search_button = ttk.Button(
    search_client_frame, text="Search", command=search_button_clicked)
search_button.pack(pady=10)

# Create a Treeview widget to display the search results
treeview = ttk.Treeview(search_client_frame)
treeview.pack(padx=10, pady=10, fill='both', expand=True)
treeview['show'] = 'tree'

# Configure the Treeview columns
treeview.column("#0", width=400)
treeview.heading("#0", text="Search Results")

# Bind the double-click event to open the folder
treeview.bind("<Double-1>", open_folder)

# Create the Notes Assistant tab
notes_assistant_tab = ttk.Frame(tab_control)
tab_control.add(notes_assistant_tab, text='Notes Assistant')


# Create a label for the client selection
client_label = Label(notes_assistant_tab, text="Select Clients:")
client_label.pack()

# Create a listbox for client selection
listbox = Listbox(notes_assistant_tab, selectmode=MULTIPLE)
listbox.pack()

populate_client_listbox()
# Create a label for the note type selection
note_type_label = Label(notes_assistant_tab, text="Select Note Type:")
note_type_label.pack()

# Create a dropdown menu for note type selection
note_type_var = StringVar(notes_assistant_tab)
note_type_var.set("")  # Set an initial value
note_type_dropdown = OptionMenu(notes_assistant_tab, note_type_var, "Skills Training (2014)", "Peer Support (0038)",
                                "Case Management (1016)")
note_type_dropdown.pack()

# Create a label for the date of service
date_of_service_label = Label(notes_assistant_tab, text="Date of Service:")
date_of_service_label.pack()

# Create an entry field for the date of service
date_of_service_entry = Entry(notes_assistant_tab)
date_of_service_entry.pack()

# Get the current date and set it as the default value in the entry field
current_date = datetime.date.today().strftime("%Y-%m-%d")
date_of_service_entry.insert(END, current_date)

# Create a label for the time selection
time_label = Label(notes_assistant_tab, text="Enter Time:")
time_label.pack()

# Create a dropdown menu for time selection
time_entry = Entry(notes_assistant_tab)
time_entry.pack()

# Create a label for the note details
note_details_label = Label(notes_assistant_tab, text="Note Details:")
note_details_label.pack()

# Create a text entry for note details
note_details_entry = Text(notes_assistant_tab, height=5, width=50)
note_details_entry.pack()

# Pass the note_type_var when calling generate_notes()
generate_button = Button(
    notes_assistant_tab, text="Generate", command=generate_notes)
generate_button.pack()

# Create the "Notes Upload" tab
notes_upload_tab = ttk.Frame(tab_control)
tab_control.add(notes_upload_tab, text='Notes Upload')

# Add the necessary widgets to the "Notes Upload" tab
sort_notes_button = ttk.Button(
    notes_upload_tab, text='Sort Notes', command=sort_notes)
sort_notes_button.pack()

# Label to display the sorting status or result
sorting_status_label = ttk.Label(notes_upload_tab, text='')
sorting_status_label.pack()

# Create the Discharge Clients tab
discharge_clients_tab = ttk.Frame(tab_control)
tab_control.add(discharge_clients_tab, text="Discharge Clients")

# Create a label for the Discharge Clients section
discharge_clients_label = Label(
    discharge_clients_tab, text="Discharge Clients")
discharge_clients_label.pack(pady=10)

# Create a listbox for client selection
discharge_listbox = Listbox(discharge_clients_tab, selectmode=MULTIPLE)
discharge_listbox.pack()

# Bind the <<ListboxSelect>> event to the on_client_selection() function
discharge_listbox.bind("<<ListboxSelect>>", on_client_selection)

# Create a button to discharge clients
discharge_button = Button(discharge_clients_tab, text="Discharge Clients",
                          command=discharge_clients_button_clicked)
discharge_button.pack(pady=10)

# Populate the discharge listbox with client names
populate_discharge_listbox()

# Bind the double-click event to open the folder
discharge_listbox.bind("<Double-1>", open_folder)
# Create the Configuration tab
config_tab = ttk.Frame(tab_control)
tab_control.add(config_tab, text='Configuration')
# Create a button to update the client list
update_button = ttk.Button(config_tab, text='Update Client List', command=lambda: [
                           populate_client_listbox(), populate_discharge_listbox()])
update_button.pack()

# Create a label for the root directory
root_directory_label = ttk.Label(config_tab, text="Root Directory:")
root_directory_label.pack(pady=10)

# Create a function to open the file dialog and update the root directory


def open_root_directory_dialog():
    global root_directory
    root_directory = filedialog.askdirectory()
    messagebox.showinfo("Root Directory Updated",
                        "Root directory has been updated successfully.")


# Create a button to update the root directory
update_root_directory_button = ttk.Button(
    config_tab, text='Update Root Directory', command=open_root_directory_dialog)
update_root_directory_button.pack(pady=10)
# Update the global variable `root_directory` with a default value
root_directory = r"D:\THC Organizational Assistant\TherapyOA\Clients"

# Create a label for the API key
api_key_label = ttk.Label(config_tab, text="API Key:")
api_key_label.pack(pady=10)

# Create an entry field for the API key
api_key_entry = ttk.Entry(config_tab, width=30)
api_key_entry.pack()

# Create a button to set the API key
api_key_button = ttk.Button(
    config_tab, text="Set API Key", command=set_api_key)
api_key_button.pack(pady=10)
if __name__ == '__main__':
    initialize_app()
# Start the main event loop
root.mainloop()
