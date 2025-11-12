import os
import re
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

def get_image_dimensions(file_path):
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except Exception:
        return (0, 0)

def get_resized_dimensions(file_path, max_size=500):
    width, height = get_image_dimensions(file_path)

    if width == 0 or height == 0:
        return (0, 0)

    longest_side = max(width, height)

    # No resizing needed
    if longest_side <= max_size:
        return (width, height)

    scale = max_size / longest_side
    new_width = int(width * scale)
    new_height = int(height * scale)

    return (new_width, new_height)

def make_lazy_load_image_link(img_path):
    display_width, display_height = get_resized_dimensions(img_path, max_size=600)
    output = f'\n<a href="{img_path}" target="_blank">'
    output += f"\n\t<img src=\"{img_path}\" alt=\"alt_text\" loading=\"lazy\" width=\"{display_width}\" height=\"{display_height}\">"
    output += f"\n</a>\n"
    return output

def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def get_jpeg_files(dir_path):
    try:
        if not os.path.isdir(dir_path):
            return []
        
        files = [
            f for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f)) and f.lower().endswith(('.jpg', '.jpeg'))
        ]

        # Natural numeric sort (e.g., 1.jpg, 2.jpg, 10.jpg)
        def numeric_key(name):
            nums = re.findall(r'\d+', name)
            return int(nums[0]) if nums else float('inf')

        files.sort(key=numeric_key)

        return [os.path.join(dir_path, f) for f in files]
    except Exception:
        return []

photo_file_paths = get_jpeg_files("./resources/photos/")


header = """

# Ratcliffe-on-Soar

A photography project about UK’s **last-remaining coal-fired power station** and its surrounding areas.

Exploring themes of legacy and change at a turning point in the industrial landscape.

-----

* **Ratcliﬀe-on-Soar** was the UK's last-remaining **coal-fired** power station.

* After 56 years of energy production, it was decommissioned in 2024.

* Its shutdown marks the end of 142 years of coal-powered electricity generation in the United Kingdom.

Email: `allen@500GX.com`

All rights reserved. I don't use social media. Beware of impersonators.

------

"""

whole_text = header + '\n'

for this_path in photo_file_paths:
    whole_text += make_lazy_load_image_link(this_path) + '<br><br>\n'


whole_text += """

----------

Project in progress.

Email: `allen@500GX.com`

----------

"""

write_to_file("README.md", whole_text)

print("written to README.md")
