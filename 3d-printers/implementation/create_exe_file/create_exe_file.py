# created by Gijs Groote on 2 aug, 2023
import PyInstaller.__main__
import os
import shutil

# Function to create folders

def main():

    # List of folder names
    folder_names = ["tom", "tim", "tam"]
    base_directory = os.path.abspath('../WACHTRIJ/')

    # remove and create empty base directory
    shutil.rmtree(base_directory)
    os.mkdir(base_directory)

    for folder_name in folder_names:
        try:
            folder_path = os.path.join(base_directory, folder_name)
            os.mkdir(folder_path)
            print(f"Folder '{folder_name}' created successfully.")

            PyInstaller.__main__.run([
                'testting.py',
                '--onefile',
                '--windowed'
                ])
            os.rename('./dist/testting', os.path.join(folder_path, 'afgekeurd'))

        except FileExistsError:
            print(f"Folder '{folder_name}' already exists.")


if __name__ == '__main__':
    main()
