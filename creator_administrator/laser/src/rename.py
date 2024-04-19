import os
import re

folder_path = 'C:\\Users\\TU Delft Metal 1520\\Desktop\\test2'

for path in os.listdir(folder_path):


    match = re.search("^.*(WB\d\d\d).*$", path)

    if match:
        groupname = match.group(1)
        
    else:
        print(f'could not find group name in {path}') 
        exit(1)


    os.rename(os.path.join(folder_path, path), os.path.join(folder_path, groupname))
