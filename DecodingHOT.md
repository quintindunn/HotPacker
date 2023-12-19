# HOT file structure.
This is how to parse a HOT file, all binary/hex is little endian.

### The file header:
#### The first 4 bytes of the file is a UTF-8/ASCII encoded string which contains: `HOT `
```
48 4F 54 20     HOT  
```
#### The next 32 bytes is 8 unsigned integers (4 bytes each), they represent the following values:
1. Unknown meaning, from my experiments this is always `0x01000000` or `1`
2. The offset of the first file's head.
3. The offset of the first file's data
4. The size of the entire file in bytes.
5. The offset for the filename table.
6. The number of files in the HOT file.
7. Unknown meaning (From my tests it is always `0x00000000`)
8. Unknown meaning (From my tests it is always `0x00000000`)

### The filename table:
The filename table starts at the offset from the header, it stores a list of every single file stored in the HOT file.
To read the filename table start at the offset given from the HOT file header, then follow this algorithm:
* Read 1 byte and if the value of the byte isn't `0x00` add it to the filename, otherwise move to the next file
* Do this for every file, the number of files is determined from the HOT file header.

### Get the file metadata:
#### To read every file's metadata:
After the first 36 bytes (First 4 containing `HOT ` + Next 32 containing file information) is the start of the file metadata table.
After those 36 bytes there will be 8 unsigned integers (4 bytes), they represent the following values:
1. The size of the file's head.
2. The offset of the file's head.
3. the size of the file minus the size of the file's head in bytes.
4. The offset of the file's data.
5. Repeat steps 1-4 `n` times (`n` being the amount of files in the HOT file defined by the header), adding 32 to the offset every iteration 

#### To read a specific file's metadata:
To get the starting `offset` use the following formula: `36 + (32 * file_index)` where file_index is the index of the file from the `filename table` starting from idx 0.
1. Read 32 bytes starting from the `starting offset`
2. Unpack this into 8 unsigned integers, (4 bytes each) they represent the following values:
(128, 32652, 22000, 0, 113280, 0, 16, 0)

   1. The size of the file's head. (`head_size`)
   2. The offset of the file's head. (`head_offset`)
   3. the size of the file minus the size of the file's head in bytes. (`file_size`)
   4. Unknown, from testing is `0`
   5. The offset of the file's data. (`data_offset`)
   6. Unknown, from testing is `0`
   7. Unknown.
   8. Unknown meaning, from testing always is `0`


### Reading/Extracting a file:
To read and extract a file you have to first get the file's metadata,
1. Check if there's a head to the file, this is from the head size from the metadata (if `head_offset` != `0x00000000` else continue to step 2)
    1. Starting from the offset of the head read the next `head_size` bytes, and store the data into memory (`head_data`).
2. Starting from the offset of the file's data read the next `file_size` bytes, and store it into memory. (`file_data`)
3. To determine the full binary data of the file simply add the `head_data` and `file_data`