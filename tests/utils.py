import os

def readfile(*in_app_path):
    path = os.path.join(*in_app_path)
    f = open(path, 'r')
    contents = f.read()
    f.close()
    return contents

def writefile(content, *in_app_path):
    path = os.path.join(*in_app_path)
    f = open(path, 'w')
    f.write(content)
    f.close()
