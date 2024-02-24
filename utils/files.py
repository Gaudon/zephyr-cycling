import uos

def list_files():
    files = uos.listdir()
    for file in files:
        print(file)
        

def read_file_as_string(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()
    return file_contents