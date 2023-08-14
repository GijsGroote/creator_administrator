import os

from executable_functions import python_to_exe
from global_variables import FUNCTIONS_DIR_HOME

def main(options_dict):
    options = {option: False for option in options_dict}

    while True:
        print("Select options:")
        for key, value in options.items():
            status = "Selected" if value else "Deselected"
            print(f"({key.upper()}) {status} {key.capitalize()}")

        choice = input("Enter option to toggle (or 'q' to quit): ").lower()

        if choice == 'q':
            break
        elif choice in options:
            options[choice] = not options[choice]
        else:
            print("Invalid option. Please choose from available options or 'q' to quit.")

if __name__ == "__main__":
    choose_option()
    available_options = ['a', 'b', 'c', 'ahahh']  # Example options list
    main(available_options)
    # python_path = os.path.join(FUNCTIONS_DIR_HOME, 'gesliced.py')
    # python_to_exe(python_path, 'Gijs_Groote')

