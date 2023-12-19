# The structure of a HOT file.

#### First 4 bytes is a string `HOT `
#### Next 32 bytes is the file's metadata, containing 8 unsigned integers with the following usages:
    1. Unknown meaning, from my experiments this is always 0x01000000 or 1
    2. The offset of the first file's head.
    3. The offset of the first file's data
    4. The size of the entire file in bytes.
    5. The offset for the filename table.
    6. The number of files in the HOT file.
    7. Unknown meaning (From my tests it is always 0x00000000)
    8. Unknown meaning (From my tests it is always 0x00000000) 

#### Next is the start of the file metadata table, for every file stored in the HOT file they contain 8 unsigned integers with the following usages:
    1. The size of the file's head. (`head_size`)
    2. The offset of the file's head. (`head_offset`)
    3. the size of the file minus the size of the file's head in bytes. (`file_size`)
    4. Unknown, from testing is `0`
    5. The offset of the file's data. (`data_offset`)
    6. Unknown, from testing is `0`
    7. Unknown.
    8. Unknown meaning, from testing always is `0`

#### Next is the start of the filename table, this contains the name of every single file stored in the HOT file. Every name is seperated by a null byte (`0x00`)

#### Next is the file head table, this contains the binary head data of every file that contains head data.

#### Next is the file data table, this contains the binary data of every file's body.
