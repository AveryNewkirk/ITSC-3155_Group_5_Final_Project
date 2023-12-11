from .config import photos

def upload_file(file):
    if file:
        filename = photos.save(file)
        return  filename
    return None