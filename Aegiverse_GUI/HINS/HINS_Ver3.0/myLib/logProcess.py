""" ####### log stuff creation, always on the top ########  """
import builtins
import inspect
import logging
import os
from datetime import datetime

if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = "record_Log"


logger = logging.getLogger(logger_name)
logger.info(logger_name + ' logger start')

""" ####### end of log stuff creation ########  """

import traceback
import win32gui
import psutil

# class functionHandler(logging.Handler):
#     # 負責接收log的資訊，傳到顯示log的UI中顯示
#     def emit(self, record):
#         log_mes = self.format(record)
#         logProcess.handle_log_message(log_mes)

class logFilter(logging.Filter):
    def filter(self, record):
        # if record.levelname in ['INFO', 'ERROR']:
        #     time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        #     # logProcess.handle_log_message(f"{time} - {record.levelname} - {record.getMessage()}")
        #     print("輸出.......")
        #     return True
        # else:
        #     return False
        def enum_handler(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                win_title = win32gui.GetWindowText(hwnd)
                if record.levelname in ['INFO', 'ERROR', 'WARNING']:
                    if "Aegiverse GUI (SG-AHRS-01-06-TTC-RW)".lower() in win_title.lower():
                        time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
                        logProcess.handle_log_message(f"{time} ； {record.levelname} ； {record.getMessage()}")
                        return True

        # if record.levelname in ['INFO', 'ERROR']:
        win32gui.EnumWindows(enum_handler, None)
        # # for processUI in psutil.process_iter(["exe", 'name']):
        # #     if "Aegiverse GUI (SG-AHRS-01-05-TTC-RW)".lower() in processUI.info["name"].lower():



class logProcess:
    __eventsLogView = None
    # 設置過濾器
    log_filter = logFilter()
    consoleHandler = logging.StreamHandler()
    # consoleHandler.setLevel(logging.DEBUG)
    # format = logging.Formatter('%(asctime)s , %(levelname)s , %(message)s')
    # consoleHandler.setFormatter(format)
    consoleHandler.addFilter(log_filter)

    __logging = logging.getLogger()
    __logging.addHandler(consoleHandler)
    # eventsView = functionHandler()
    # format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # eventsView.setFormatter(format)
    # __logging.addHandler(eventsView)
    #
    # consoleHandler = logging.StreamHandler()
    # consoleHandler.setLevel(logging.DEBUG)
    # consoleHandler.addFilter(logFilter())

    @staticmethod
    def fileStartedInfo(logName, mes):
        __logger = logging.getLogger(logName +"."+ mes)
        __logger.info(mes  + ' logger start')

        # eventsView = functionHandler()
        # __logger.addHandler(eventsView)
        # logProcess._logProcess__eventsLogView.creat_info_view()

    @staticmethod
    def setVariable(obj):
        logProcess.__eventsLogView = obj
        print("func: ",obj)

    @staticmethod
    def handle_log_message(message):
        logProcess.__eventsLogView.split_log_info(message)
        print(f"輸入的訊息：{message}")

    # @staticmethod
    # def centrailzedError(err, content="", fileName=""):
    #     # # 取得發生錯誤的軌跡
    #     errTrace = traceback.format_exc()
    #     splitTrace = errTrace.split("\n")
    #
    #     #logger.error(f'error occurred in: {splitTrace}')
    #
    #     errPath = inspect.stack()[1].lineno
    #     # strTrace = splitTrace[-2] + ", line " + str(errPath)
    #     # logger.error(strTrace)
    #
    #     __logger_err = logging.getLogger(logger_name + "." + fileName)
    #     __logger_err.error(f'{str(err)}--{content}'+ ", line " + str(errPath))

    # 給其他未設定要傳送資料的function使用
    @staticmethod
    def receive(logName, num, fileName, error):
        tb = error.__traceback__  # 錯誤軌跡資訊
        if str(type(error).__name__) == "NameError":
            logProcess.centrailzedError(logName=logName, num=num, fileName=fileName, content=f"NameError — Variable name is not defined", line=tb.tb_lineno)
        elif str(type(error).__name__) == "AttributeError":
            logProcess.centrailzedError(logName=logName, num=num, fileName=fileName, content=f"AttributeError — The attribute currently in use does not exist in the object", line=tb.tb_lineno)
        else:
            logProcess.centrailzedError(logName=logName, num=num, fileName=fileName, content=f"{str(type(error).__name__)} — " + str(error), line=tb.tb_lineno)

    @staticmethod
    def centrailzedError(logName, num, fileName="", content="", line=""):
        __logger_err = logging.getLogger(logName + "." + fileName)
        __logger_err.error(f'[{str(num)}] {content}'+ ", line " + str(line)+'.')


    @staticmethod
    def centrailzedInfo(logName, mes, fileName):
        __logger_info = logging.getLogger(logName + "." + fileName)
        __logger_info.info(mes)

    @staticmethod
    def centrailzedWarning(logName, content="", fileName=""):
        __logger_warn = logging.getLogger(logName + "." + fileName)
        __logger_warn.warning(content)

    @staticmethod
    def centrailzedDebug(logName, err, content="", fileName=""):
        debugTrace = traceback.format_exc()
        splitTrace = debugTrace.split("\n")

        debugPath = splitTrace[1].split(",")
        # strTrace = splitTrace[-2]+ "," + debugPath[1]
        # logger.debug(strTrace)

        __logger_debug = logging.getLogger(logName + "." + fileName)
        __logger_debug.debug(f'{str(err)}--{content}' + "," + debugPath[1])

    # 提供給開發者確認會跳出的debug function，或是想知道是否有錯誤但except判斷不到。
    @staticmethod
    def checkInfoDebug(logName, content="", fileName=""):
        __logger_infoDebug = logging.getLogger(logName + "." + fileName)
        __logger_infoDebug.debug(content)

# def centrailzedError(self,err, content="", fileName=""):
#         # # 取得發生錯誤的軌跡
#         errTrace = traceback.format_exc()
#         splitTrace = errTrace.split("\n")
#
#         #logger.error(f'error occurred in: {splitTrace}')
#
#         errPath = inspect.stack()[1].lineno
#         # strTrace = splitTrace[-2] + ", line " + str(errPath)
#         # logger.error(strTrace)
#
#         __logger_err = logging.getLogger(__logger_name + "." + fileName)
#         __logger_err.error(f'{str(err)}--{content}'+ ", line " + str(errPath))
#
#
# def centrailzedInfo(self, mes, fileName):
#         __logger_info = logging.getLogger(__logger_name + "." + fileName)
#         __logger_info.info(mes)
#
#
# def centrailzedWarning(self, content="", fileName=""):
#         __logger_warn = logging.getLogger(__logger_name + "." + fileName)
#         __logger_warn.warning(content)
#
#
# def centrailzedDebug(self, err, content="", fileName=""):
#         debugTrace = traceback.format_exc()
#         splitTrace = debugTrace.split("\n")
#
#         debugPath = splitTrace[1].split(",")
#         # strTrace = splitTrace[-2]+ "," + debugPath[1]
#         # logger.debug(strTrace)
#
#         __logger_debug = logging.getLogger(__logger_name + "." + fileName)
#         __logger_debug.debug(f'{str(err)}--{content}' + "," + debugPath[1])



