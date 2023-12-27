"""
Communicate with Student Assistant (SA).
"""
import os
import re

from typing import Tuple
from global_variables import gv

from src.talk_to_sa import choose_one_option
from src.directory_functions import get_prefix_of_subfolders

def enter_material_thickness_amount(file_name) -> Tuple[str, str, str]:
    """ Return strings for material, thickness and amount. """
    material = choose_one_option(f'What material is: {file_name}?',
                get_prefix_of_subfolders(os.path.join(gv['JOBS_DIR_HOME'], 'WACHTRIJ_MATERIAAL')),
                options_type='material')

    while True:
        thickness = choose_one_option(f'\nWhat thickness is: {file_name}?',
                    [], options_type='thickness')
        if not thickness.endswith('mm'):
            thickness = thickness+'mm'
        thickness = thickness.replace(',', '.')
        
        if re.search(r'^[0-9]*[.]{0,1}[0-9]*mm$', thickness):
            break
        else:
            print(f'could not convert {thickness} to a decimal number, try again')

    try:
        amount = input('amount (default=1)?')
        amount = str(int(amount))
    except Exception as e:
        amount = '1'
    
    return material, thickness, amount