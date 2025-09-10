""" ####### log stuff creation, always on the top ########  """
import builtins
import inspect
import logging

logger_name = "recordLog"
if hasattr(builtins, 'LOGGER_NAME'):
    logger_name = builtins.LOGGER_NAME
else:
    logger_name = "recordLog"


logger = logging.getLogger(logger_name)
logger.info(__name__ + ' logger start')
""" ####### end of log stuff creation ########  """

import traceback



class logProcess:
    def centrailzedError(self,err, content="", fileName=""):
        # # 取得發生錯誤的軌跡
        errTrace = traceback.format_exc()
        splitTrace = errTrace.split("\n")

        #logger.error(f'error occurred in: {splitTrace}')

        errPath = inspect.stack()[1].lineno
        # strTrace = splitTrace[-2] + ", line " + str(errPath)
        # logger.error(strTrace)

        logger_err = logging.getLogger(logger_name + "." + fileName)
        logger_err.error(f'{str(err)}--{content}'+ ", line " + str(errPath))


    def centrailzedInfo(self, mes, fileName):
        logger_info = logging.getLogger(logger_name + "." + fileName)
        logger_info.info(mes)


    def centrailzedWarning(self, content="", fileName=""):
        logger_warn = logging.getLogger(logger_name + "." + fileName)
        logger_warn.warning(content)


    def centrailzedDebug(self, err, content="", fileName=""):
        debugTrace = traceback.format_exc()
        splitTrace = debugTrace.split("\n")

        debugPath = splitTrace[1].split(",")
        # strTrace = splitTrace[-2]+ "," + debugPath[1]
        # logger.debug(strTrace)

        logger_debug = logging.getLogger(logger_name + "." + fileName)
        logger_debug.debug(f'{str(err)}--{content}' + "," + debugPath[1])





