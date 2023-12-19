def get_head_size(file_ext: str):
    """
    Determines the size of the header for a given file extension
    :param file_ext:
    :return:
    """
    if file_ext in {"dds"}:
        return 128
    if file_ext in {"wav"}:
        return 72

    return 0
