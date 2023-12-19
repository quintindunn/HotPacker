def get_head_size(file_ext: str):
    if file_ext in {"dds"}:
        return 128
    if file_ext in {"wav"}:
        return 72

    return 0