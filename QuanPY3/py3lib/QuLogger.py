import logging

format="%(levelname)s: %(module)s, %(threadName)s, %(thread)d, %(message)s"
formater = logging.Formatter(format)

def QuConsolelogger(loggername, level):	
	streamH = logging.StreamHandler()
	logger = logging.getLogger(loggername)
	streamH.setFormatter(formater)
	logger.addHandler(streamH)
	logger.setLevel(level)

def QuFilelogger(loggername, level, fname):
	fileH = logging.FileHandler(fname, 'w+')
	logger = logging.getLogger(loggername)
	fileH.setFormatter(formater)
	logger.addHandler(fileH)
	logger.setLevel(level)

