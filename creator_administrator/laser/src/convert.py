import re

def split_material_name(material_name) -> tuple[str, str]:
    ''' Split material name (such as steel_3mm) into steel and 3. '''

    match = re.search(r'(.+)_([\d.]+)mm', material_name)
    if match:
        material = match.group(1)
        thickness = match.group(2)
        return material, thickness
    raise ValueError(f'could not split {material_name}')


