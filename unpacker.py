import struct
import os
import zlib

file = input("File name: ") or "textures.hot"

name = os.path.basename(file).split(".")[0]

# If output directory doesn't exist, create it.
if not os.path.exists(os.getcwd() + "/OUTPUT/" + name + "/"):
    os.makedirs(os.getcwd() + "/OUTPUT/" + name + "/")

outPath = os.getcwd() + "/OUTPUT/" + name + "/"

with open(file, "rb") as f:
    # Validate the file is a HOT file.
    fileString = f.read(4).decode("UTF-8")
    if fileString != "HOT ":
        raise ValueError("File is not a HOT file.")

    # Unpack the header of the file (bytes 5-32) and unpack it into unsigned integers (little endian).
    # Unsigned integer is 4 bytes (8*"I")
    headerInfo = struct.unpack('<IIIIIIII', f.read(0x20))

    first_file_head_offset = headerInfo[1]  # The offset of the first file's head.
    overall_file_size = headerInfo[3]  # The size of the .hot file in bytes.
    filename_table_offset = headerInfo[4]  # The offset where the list of files begin
    file_count = headerInfo[5]  # The number of files encoded into the hot file.

    print(f"Header info: {headerInfo}")

    next_header_start_offset = f.tell()

    files = []

    f.seek(filename_table_offset - 1)

    for _ in range(file_count):
        filename = []

        # Read the next character, if the data == 0x00000000 then go on to the next file.
        character = f.read(1)

        while character != 0:
            character = f.read(1)[0]
            if character != 0:
                filename.append(chr(character))

        while character == 0:  # Read until the next name starts.
            character = f.read(1)[0]

        if len(filename) != 0:  # If there is a valid filename, add it to the list of filenames
            files.append(''.join(filename))

        # Go back two bytes relative to the current idx we're reading to counteract the initial read
        # and the read until the next character
        f.seek(-2, 1)

    for filename in files:
        f.seek(next_header_start_offset)
        print(next_header_start_offset)

        # Unpack the header of the file (first 32 bytes) and unpack it into unsigned integers (little endian).
        # Unsigned integer is 4 bytes (8*"I")
        fileInfo = struct.unpack('<IIIIIIII', f.read(32))
        headSize = fileInfo[0]  # The size of the file's head
        headOffset = fileInfo[1]  # The offset of the file's head
        fileSize = fileInfo[2]  # The size of the file's data
        fileOffset = fileInfo[4]  # The offset of the file's data

        print(filename, *fileInfo)

        next_header_start_offset = f.tell()

        # Read the head data
        f.seek(headOffset)
        head_data = f.read(headSize)

        # Read the body data
        f.seek(fileOffset)
        body_data = f.read(fileSize)

        # Some files are compressed, decompress those files.
        if name.lower() in ("modelsandanims", "world"):
            DATA = head_data + body_data
            head_data = zlib.decompress(DATA)
            print(f"File of type \"{name.lower()}\" decompressed.")

        with open(outPath + filename, "w+b") as output_file:
            output_file.write(head_data)

            if name.lower() not in ("modelsandanims", "world"):
                output_file.write(body_data)
