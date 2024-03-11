import chardet

def get_csv_encoding(file_path):
    # Determine the encoding of the file
    rawdata = open(file_path, 'rb').read()
    result = chardet.detect(rawdata)
    return result['encoding']