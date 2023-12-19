from io import BytesIO

import os
import struct

from head_sizes import get_head_size

file_name = input("File name: ") or "textures_new.hot"
files_dir = input("Files Dir: ") or "./OUTPUT/textures"

files = os.listdir(files_dir)


class HOTFile:
    def __init__(self, input_dir: str):
        self.file_names = os.listdir(input_dir)
        self.files_root = input_dir

        self.header = "HOT ".encode("utf-8")

