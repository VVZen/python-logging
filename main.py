import os
import logging
import logging.handlers

################################################################################
# @brief      Setup the logging to console and to file (one log for day)
# @details    
# @args       
# @return     None
#

logger = logging.getLogger()

def init_logger(outputDir):

    logger.setLevel(logging.DEBUG)

    # create console handler and set level to DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter("%(asctime)s-%(filename)s:%(lineno)s@%(funcName)s() : %(message)s")

    logger.addHandler(console_handler)

    # create error file handler and set level to error
    error_handler = logging.FileHandler(os.path.join(outputDir, "name.error.log"), "w")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # create debug file handler and set level to debug
    file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(outputDir, "name.log"), "midnight", 1, 7)
    file_handler.setLevel(logging.DEBUG)
    # file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
