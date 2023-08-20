#! /usr/bin/env python3
import os.path
import shutil
import sys

if __name__ == '__main__':
    remove_dir_global_path = sys.argv[1]
    remove_dir_global_path = r'C:\Users\gijsg\Desktop\3D PRINT HOME\WACHTRIJ\20-08_GSGroote'
    print(f'removing this: {remove_dir_global_path}, which is a folder: {os.path.isdir(remove_dir_global_path)}')
    shutil.rmtree(remove_dir_global_path)