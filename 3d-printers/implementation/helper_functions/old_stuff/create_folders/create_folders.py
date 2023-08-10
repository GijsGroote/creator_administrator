import os
import shutil

def main():

    # Function to create folders
    folder_names = ["tom", "tim", "tam"]
    base_directory = os.path.abspath('../../WACHTRIJ/')

    # remove and create empty base directory
    shutil.rmtree(base_directory)
    os.mkdir(base_directory)

    for folder_name in folder_names:
        try:
            folder_path = os.path.join(base_directory, folder_name)
            os.mkdir(folder_path)
            print(f"Folder '{folder_name}' created successfully.")

        except FileExistsError:
            print(f"Folder '{folder_name}' already exists.")


if __name__ == '__main__':
    main()
