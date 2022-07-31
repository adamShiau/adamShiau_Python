import sys
from datetime import datetime
import time
from os.path import exists
import os

sys.path.append("../../")
from myLib import common as cmn


class atSave_PC:

    def __init__(self, fnum=0):
        # self.__name = None
        self.__data_manager = cmn.data_manager(fnum=fnum)
        self.hh_path = None
        # self.data_path = rootPath + '/' + 'data'
        self.__data_path = None
        self.dd_path = None
        self.mm_path = None
        self.yy_path = None
        # self.__is_empty_folder = True
        self.start = True
        # self.__start = True

    def create_data_folder(self, en=False):
        if en:
            print('data path: ', self.data_path)
            file_exist = exists(self.data_path)
            print('data folder exist? : ', file_exist)
            if not file_exist:
                # self.__is_empty_folder = True
                os.mkdir(self.data_path, mode=0o777)
                print('     create data folder done.')

    def create_year_folder(self):
        yy = datetime.now().year
        self.yy_path = self.data_path + '/' + str(yy)
        file_exist = exists(self.yy_path)
        # print('year folder %s exist?: %s' % (self.yy_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.yy_path, mode=0o777)
            print('     create year folder %d done.' % yy)

    def create_month_folder(self):
        mm = datetime.now().month
        self.mm_path = self.yy_path + '/' + str(mm)
        file_exist = exists(self.mm_path)
        # print('month folder %s exist?: %s' % (self.mm_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.mm_path, mode=0o777)
            print('     create month folder %d done.' % mm)

    def create_day_folder(self):
        dd = datetime.now().day
        self.dd_path = self.mm_path + '/' + str(dd)
        file_exist = exists(self.dd_path)
        # print('day folder %s exist?: %s' % (self.dd_path, file_exist))
        if not file_exist:
            # self.__is_empty_folder = True
            os.mkdir(self.dd_path, mode=0o777)
            print('     create day folder %d done.' % dd)

    def auto_create_folder(self, en=False):
        if en:
            self.create_year_folder()
            self.create_month_folder()
            self.create_day_folder()
            self.open_hour_file()

    def open_hour_file(self):
        hh = datetime.now().hour
        self.hh_path = self.dd_path + '/' + str(hh) + '.txt'
        file_exist = exists(self.hh_path)
        # print('hour file %d.txt exist?: %s' % (hh, file_exist))
        if file_exist:
            if self.start:
                os.remove(self.hh_path)
                print('     remove hour file %d.txt done.' % hh)
                self.__data_manager.name = self.hh_path
                self.__data_manager.open(True)
                self.start = False
                print('     re-create hour file %d done.' % hh)

        else:
            if self.start:
                self.start = False
            else:
                self.close_hour_folder()
                print('     close hour file %d done.' % (hh - 1))
            self.__data_manager.name = self.hh_path
            self.__data_manager.open(True)
            print('     create hour file %d done.' % hh)

            # if self.__is_empty_folder and (not self.__start):
            #     self.close_hour_folder()
            #     self.__is_empty_folder = False
            # self.__data_manager.name = self.hh_path
            # self.__data_manager.open(True)
            # print('     create hour file %d done.' % hh)

    def close_hour_folder(self):
        self.__data_manager.close()
        pass

    def write_line(self, comment):
        self.__data_manager.write_line(comment)

    def saveData(self, datalist, fmt):
        self.__data_manager.saveData(datalist, fmt)

    @property
    def data_path(self):
        return self.__data_path + '/' + 'data'

    @data_path.setter
    def data_path(self, path):
        self.__data_path = path

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, val):
        self.__start = val


if __name__ == "__main__":
    t = atSave_PC()
