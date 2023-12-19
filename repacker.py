from head_sizes import get_head_size

from io import BytesIO

import os
import struct

file_name = input("File name: ") or "out.hot"
files_dir = input("Files Dir: ") or "./OUTPUT/textures"

files = os.listdir(files_dir)

FORMAT = "utf-8"


class PackedData:
    def __init__(self):
        self.size = 32

    def packed(self):
        ...


class FileMetadataItem(PackedData):
    def __init__(self, filename: str, head_size: int = 0, head_offset: int = 0, data_size: int = 0, unknown_0: int = 0,
                 data_offset: int = 0, unknown_1: int = 0, unknown_2: int = 99, unknown_3: int = 0):
        super().__init__()

        self.filename = filename

        self.head_size = head_size
        self.head_offset = head_offset
        self.data_size = data_size
        self.unknown_0 = unknown_0
        self.data_offset = data_offset
        self.unknown_1 = unknown_1
        self.unknown_2 = unknown_2  # tbd
        self.unknown_3 = unknown_3

    def packed(self):
        return struct.pack("<IIIIIIII",
                           self.head_size, self.head_offset, self.data_size, self.unknown_0, self.data_offset,
                           self.unknown_1, self.unknown_2, self.unknown_3)


class CoreMetadata(PackedData):
    def __init__(self, filename: str, unknown_0: int = 0, first_file_head_offset: int = 0, unknown_1: int = 0,
                 file_size: int = 0, filename_table_offset: int = 0, file_count: int = 0):
        super().__init__()

        self.filename = filename

        self.unknown_0 = unknown_0
        self.first_file_head_offset = first_file_head_offset
        self.unknown_1 = unknown_1
        self.file_size = file_size
        self.filename_table_offset = filename_table_offset
        self.file_count = file_count

    def packed(self):
        return struct.pack("<IIIIIIII",
                           self.unknown_0, self.first_file_head_offset, self.unknown_1, self.file_size,
                           self.filename_table_offset,
                           self.file_count, 0, 0)


class HOTFile(PackedData):
    NULL_BYTE = struct.pack("B", 0)

    def __init__(self, input_dir: str):
        super().__init__()

        self.content = []

        self.file_names = os.listdir(input_dir)
        self.files_root = input_dir

    def generate_filename_table(self):
        table_content = BytesIO()
        for file in self.file_names:
            table_content.write(file.encode(FORMAT))

            null_byte_count = (4 - len(file) % 4) or 4
            for _ in range(null_byte_count):
                table_content.write(self.NULL_BYTE)

        return table_content.getvalue()

    def generate_metadata_placeholder(self):
        metadata_items = []
        for file in self.file_names:
            file_path = os.path.join(self.files_root, file)
            file_head_size = get_head_size(file.split(".")[-1])

            real_file_size = os.path.getsize(file_path)
            embedded_file_size = real_file_size - file_head_size

            metadata_item = FileMetadataItem(filename=file, head_size=file_head_size, data_size=embedded_file_size)
            metadata_items.append(metadata_item)
        return metadata_items

    def generate_head_table(self):


    def build(self):
        # Add "HOT " prefix to file
        self._write("HOT ".encode(FORMAT))

        # Generate the metadata for the actual file
        self._write(CoreMetadata(filename=file_name, file_count=len(self.file_names)))

        # Generate the metadata for the subfiles
        for file_metadata in self.generate_metadata_placeholder():
            self._write(file_metadata)

        # Generate the filename table
        for byte in list(self.generate_filename_table()):
            self._write(byte)

    def calculate_offset(self, real_idx: int | None = None):
        if real_idx is None:
            real_idx = len(self.content) - 1

        offset = 0
        for i in range(0, real_idx + 1):
            i = self.content[i]
            if isinstance(i, bytes) or isinstance(i, int):
                offset += 1
            elif isinstance(i, PackedData):
                offset += i.size
        return offset

    def _write(self, content, idx: int | None = None):
        if idx is not None:
            return self.content.insert(idx, content)
        return self.content.append(content)

    def to_io(self):
        io = BytesIO()
        for byte_data in self.content:
            if isinstance(byte_data, bytes):
                io.write(byte_data)
            elif isinstance(byte_data, PackedData):
                io.write(byte_data.packed())
            elif isinstance(byte_data, int):
                io.write(chr(byte_data).encode(FORMAT))
        return io


if __name__ == '__main__':
    hot = HOTFile(input_dir=files_dir)
    hot.build()

    with open("out.hot", 'wb') as f:
        f.write(hot.to_io().getvalue())
