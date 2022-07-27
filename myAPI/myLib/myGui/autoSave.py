from datetime import datetime
import time
from os.path import exists
import os


class atSave_PC:

    def __init__(self, rootPath='.', actObj=None):
        self.hh_path = None
        self.data_path = rootPath + '/' + 'data'
        self.dd_path = None
        self.mm_path = None
        self.yy_path = None

        self.create_data_folder()
        self.create_year_folder()
        self.create_month_folder()
        self.create_day_folder()
        t1 = time.perf_counter_ns()
        self.open_hour_file()
        t2 = time.perf_counter_ns()
        print((t2-t1)*1e-3)

    def create_data_folder(self):
        file_exist = exists(self.data_path)
        print('data folder exist? : ', file_exist)
        if not file_exist:
            os.mkdir(self.data_path, mode=0o777)
            print('     create data folder done.')

    def create_year_folder(self):
        yy = datetime.now().year
        self.yy_path = self.data_path + '/' + str(yy)
        file_exist = exists(self.yy_path)
        print('year folder %d exist?: %s' % (yy, file_exist))
        if not file_exist:
            os.mkdir(self.yy_path, mode=0o777)
            print('     create year folder %d done.' % yy)

    def create_month_folder(self):
        mm = datetime.now().month
        self.mm_path = self.yy_path + '/' + str(mm)
        file_exist = exists(self.mm_path)
        print('month folder %d exist?: %s' % (mm, file_exist))
        if not file_exist:
            os.mkdir(self.mm_path, mode=0o777)
            print('     create month folder %d done.' % mm)

    def create_day_folder(self):
        dd = datetime.now().day
        self.dd_path = self.mm_path + '/' + str(dd)
        file_exist = exists(self.dd_path)
        print('day folder %d exist?: %s' % (dd, file_exist))
        if not file_exist:
            os.mkdir(self.dd_path, mode=0o777)
            print('     create day folder %d done.' % dd)

    def open_hour_file(self):
        hh = datetime.now().hour
        self.hh_path = self.dd_path + '/' + str(hh)
        file_exist = exists(self.hh_path)
        print('hour file %d exist?: %s' % (hh, file_exist))
        if not file_exist:
            # os.mkdir(self.dd_path, mode=0o777)
            print('     create hour file %d done.' % hh)


if __name__ == "__main__":
    t = atSave_PC()
