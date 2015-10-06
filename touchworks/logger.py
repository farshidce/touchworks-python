import logging
import logging.config


class Logger(object):
    @staticmethod
    def get_logger(name):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - ' +
                                      '%(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger
