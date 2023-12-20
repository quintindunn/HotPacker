import json

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
    def __init__(self, filename: str, unknown_0: int = 0, first_file_head_offset: int = 0, file_data_table_start: int = 0,
                 file_size: int = 0, filename_table_offset: int = 0, file_count: int = 0):
        super().__init__()

        self.filename = filename

        self.unknown_0 = unknown_0
        self.first_file_head_offset = first_file_head_offset
        self.file_data_table_start = file_data_table_start
        self.file_size = file_size
        self.filename_table_offset = filename_table_offset
        self.file_count = file_count

    def packed(self):
        return struct.pack("<IIIIIIII",
                           self.unknown_0, self.first_file_head_offset, self.file_data_table_start, self.file_size,
                           self.filename_table_offset,
                           self.file_count, 0, 0)


class HOTFile(PackedData):
    NULL_BYTE = b'\x00'

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

    def add_head_table(self):
        first_head_item = True
        core_meta = None
        for head_item in self.content:
            if isinstance(head_item, CoreMetadata):
                core_meta = head_item
                continue
            elif not isinstance(head_item, FileMetadataItem):
                continue

            if head_item.head_size == 0:
                continue

            file_path = os.path.join(self.files_root, head_item.filename)
            with open(file_path, 'rb') as embedded_item:
                head_content = embedded_item.read(head_item.head_size)
                print(head_item.head_size, len(head_content))

            head_item.head_offset = self.calculate_offset()

            if first_head_item:
                first_head_item = False
                core_meta.first_file_head_offset = head_item.head_offset

            for byte in head_content:
                self._write(byte)

        for _ in range(4):
            self._write(b"\x00")

        core_meta.file_data_table_start = self.calculate_offset()

    def add_data_table(self):
        for head_item in self.content:
            if not isinstance(head_item, FileMetadataItem):
                continue

            print(head_item.filename, "Packing...")

            if head_item.data_size == 0:
                continue

            file_path = os.path.join(self.files_root, head_item.filename)
            head_item.data_offset = self.calculate_offset()

            with open(file_path, 'rb') as embedded_item:
                file_data = embedded_item.read(head_item.data_size)
                self._write(file_data)

        for _ in range(4):
            self._write(b"\x00")

    def build(self):
        # Add "HOT " prefix to file
        self._write("HOT ".encode(FORMAT))

        # Generate the metadata for the actual file
        core_meta = CoreMetadata(filename=file_name, file_count=len(self.file_names))
        self._write(core_meta)

        # Generate the metadata for the subfiles
        for file_metadata in self.generate_metadata_placeholder():
            self._write(file_metadata)

        core_meta.filename_table_offset = self.calculate_offset()

        # Generate the filename table
        for byte in list(self.generate_filename_table()):
            self._write(byte)

        # Generate the head table
        self.add_head_table()

        # Generate the data table
        self.add_data_table()

    def calculate_offset(self, real_idx: int | None = None):
        if real_idx is None:
            real_idx = len(self.content) - 1

        offset = 0
        for i in range(0, real_idx + 1):
            i = self.content[i]
            if isinstance(i, bytes):
                offset += len(i)
            elif isinstance(i, int):
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

    print("Saving output...")
    with open("out.hot", 'wb') as f:
        f.write(hot.to_io().getvalue())
