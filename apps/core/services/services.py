import os 


def delete_file_from_media(file):
    if file and os.path.isfile(file.path):
        os.remove(file.path)