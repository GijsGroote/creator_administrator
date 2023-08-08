import os
import shutil

def move_files_recursively(source_dir, destination_dir):
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)

        if os.path.isdir(source_item):
            shutil.move(source_item, destination_item)
            move_files_recursively(source_item, destination_item)
        else:
            shutil.move(source_item, destination_dir)

def main():

    old_folder_path = os.path.dirname(os.path.abspath(__file__))


    if old_folder_path.endswith("AFGEKEURD/naam"):
        new_folder_path = "../../WACHTRIJ/naam"

    elif old_folder_path.endswith("WACHTRIJ/naam"):
        new_folder_path = ""

    else:
        print("could not recognise")
        raise ValueError("Could not recognise")

    os.mkdir(new_folder_path)

    move_files_recursively(old_folder_path, new_folder_path)

    shutil.rmtree(old_folder_path)

if __name__ == '__main__':
    main()
