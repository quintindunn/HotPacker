from io import BytesIO

import os
import struct

file_name = input("File name: ") or "out.hot"
files_dir = input("Files Dir: ") or "./OUTPUT/textures"

files = os.listdir(files_dir)


class HOTFile:
    def __init__(self, input_dir: str):
        self.file_names = os.listdir(input_dir)
        self.files_root = input_dir

        self.content = []

        self._write("HOT ".encode('utf-8'))

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
    hot._write(struct.pack("<IIIIIIII", 1, 2, 3, 4, 5, 6, 7, 8))

    with open(file_name, 'wb') as f:
        f.write(hot.to_io().getvalue())
