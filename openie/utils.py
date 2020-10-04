def text_file_to_list(file_name):
    with open(file_name) as f:
        result = list(f)
    return result
