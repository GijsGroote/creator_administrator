"""
Gcode File Organizer
--------------------

The script reads through a specified folder sorts them based on the parsed time and saves the information to a CSV file.

Requirements:
- Python 3.x

Usage:
1. Specify the folder path where the Gcode files are located.
2. Specify the output file path for the CSV file.
3. Run the script.

"""
import csv
from datetime import datetime
import os


def main():
    """
        Reads through the specified folder, identifies Gcode files,
        sorts them based on the parsed time in their names, and saves the information to a CSV file.
    """
    folder_path = "C://Users/IWS/Desktop/3D TO DO/Wachtrij"  # Folder where the gcodes are located
    g_codes = []
    skip_list = ["VERWERKT"]  # Add the folder name you do not want checked in this list.

    for root, dirs, files in os.walk(folder_path):
        if any(skip_item in root for skip_item in skip_list):  # Skip unwanted folders
            continue
        temp_gcodes = append_times(files, root)  # Use a temporary list for appending values
        g_codes.extend(temp_gcodes)  # Extend the gcodes list with values from the temporary list

    g_codes.sort(key=lambda x: parse_time(x[0]), reverse=False)    # Sort based on parsed time
    save_all_csv(g_codes)


def append_times(files, root):
    """
    Returns a list of all durations of gcodes and the absolute path.
    """
    g_codes = []
    for name in files:
        if name.endswith('.gcode'):
            name = name.split("_")[0]
            folder = os.path.abspath(root)
            g_codes.append((name, folder))
    return g_codes


def save_all_csv(rows):
    """
    save all rows of the g codes list into a CSV at specified output paths
    """
    output_file = "C://Users/IWS/Desktop/Wachtrij.csv"
    wachtrij_file = "C://Users/IWS/Desktop/3D TO DO/Wachtrij/Wachtrij.csv"

    save_to_csv(rows, output_file, encoding='utf-8')
    save_to_csv(rows, wachtrij_file, encoding='utf-8')


def parse_time(time_str):  # Sort the files based on time
    """
        Parses the time in the Gcode file name and returns it in minutes.

        Args:
            time_str (str): The time string to be parsed.

        Returns:
            int: The parsed time in minutes.

    """
    try:
        if 'd' in time_str:
            days, time = time_str.split('d')
            hours, minutes = time.split('h')
            total_hours = int(days) * 24 + int(hours)
            total_minutes = total_hours * 60 + int(minutes)
            return total_minutes
        elif 'h' in time_str and 'm' in time_str:
            time = datetime.strptime(time_str, "%Hh%Mm").time()
            total_minutes = time.hour * 60 + time.minute
            return total_minutes
        elif 'm' in time_str:
            minutes = time_str[:-1]  # Remove the 'm' suffix
            total_minutes = int(minutes)
            return total_minutes
        else:
            return float('inf')  # Return positive infinity for invalid format
    except ValueError:
        return float('inf')  # Return positive infinity for invalid format


def save_to_csv(data, output, encoding='utf-8'):
    """
        Writes the provided data to a CSV file.

        Args:
            data (list): The data to be written to the CSV file.
            output (str): Path to the output CSV file.
            encoding (str, optional): The encoding of the CSV file. Defaults to 'utf-8'.

    """
    with open(output, 'w', newline='', encoding=encoding) as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Folder Path'])
        for name, folder in data:
            hyperlink = create_hyperlink(folder)
            writer.writerow([name, hyperlink])


def create_hyperlink(folder):
    """
        Creates a hyperlink formula for the given folder path.

        Args:
            folder (str): The folder path for the hyperlink.

        Returns:
            str: The hyperlink formula.

    """
    folder_name = os.path.basename(folder)  # Get the base folder name
    return f'=HYPERLINK("{folder}", "{folder_name}")'


main()
