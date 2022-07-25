from datetime import datetime
import time
from os.path import exists
import os


class atSave_PC:

    def __init__(self, rootPath='./', actObj=None):
        file_exist = exists(rootPath + 'data')
        print(file_exist)
        os.mkdir(rootPath + 'data', mode=0o777)
        # print(datetime.now().second)


if __name__ == "__main__":
    atSave_PC()