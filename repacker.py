import textwrap
from io import BytesIO

import os
import struct

file_name = input("File name: ") or "out.hot"
files_dir = input("Files Dir: ") or "./OUTPUT/textures"

files = os.listdir(files_dir)

FORMAT = "utf-8"


class HOTFile:
    NULL_BYTE = struct.pack("B", 0)

    def __init__(self, input_dir: str):
        self.file_names = os.listdir(input_dir)
        self.files_root = input_dir

        self.content = []

    def generate_filename_table(self):
        table_content = BytesIO()
        for file in self.file_names:
            table_content.write(file.encode(FORMAT))

            null_byte_count = (4 - len(file) % 4) or 4
            for _ in range(null_byte_count):
                table_content.write(self.NULL_BYTE)

        return table_content.getvalue()

    def build(self):
        self._write("HOT ".encode(FORMAT))
        self._write(self.generate_filename_table())

    def _write(self, content, idx: int | None = None):
        if idx is not None:
            return self.content.insert(idx, content)
        return self.content.append(content)

    def to_io(self):
        io = BytesIO()
        io.write(b''.join(self.content))
        return io


if __name__ == '__main__':

    hot = HOTFile(input_dir=files_dir)
    hot.build()

    with open("out.hot", 'wb') as f:
        f.write(hot.to_io().getvalue())
