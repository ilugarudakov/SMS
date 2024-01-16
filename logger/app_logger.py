import logging
from config import Config

# create logger
logger = logging.getLogger('AppFileLogger')
logger.setLevel(logging.INFO)
# create file handler and set level to debug
# filepath = os.path.abspath(os.path.join(os.pardir, "files", 'logs', 'smsserver.log'))
filepath = Config.logpath()
fh = logging.FileHandler(filename=filepath)
# fh.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
# add formatter to fh
fh.setFormatter(formatter)
# add fh to logger
logger.addHandler(fh)
# 'application' code

# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')