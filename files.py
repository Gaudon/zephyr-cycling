import uos


def list_files():
    files = uos.listdir()
    for file in files:
        print(file)