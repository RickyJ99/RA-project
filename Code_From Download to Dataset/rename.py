import os


folder_path = "Code_From Download to Dataset/Resources/folder"


# Check if the folder exists
if not os.path.exists(folder_path):
    print(f"Folder '{folder_path}' does not exist.")
else:
    # List all files in the folder
    files = os.listdir(folder_path)

    # Sort the files based on the timestamp part of the filename
    files.sort(key=lambda x: x.split("-")[-1].replace("28T", "").split(".")[0])
    # files.sort(key=lambda x: int(x.split("(")[-1].split(")")[0]))
    # Initialize the renaming index
    i = 0

    # Iterate through the sorted files and rename them
    for filename in files:
        # Skip renaming the .DS_Store file
        if filename == ".DS_Store":
            continue

        # Generate the new filename
        new_filename = f"CohMetrixOutput ({i+165}).txt"

        # Get the full path of the file
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)

        # Rename the file
        os.rename(old_file_path, new_file_path)
        print(f"Renamed '{filename}' to '{new_filename}'")

        # Increment the index
        i += 1

print("Renaming completed.")
