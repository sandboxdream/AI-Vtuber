import logging

def Configure_logger(log_file):
    # log_format = "%(asctime)s - %(levelname)s - %(message)s"
    log_format = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='a+')
    stream_handler = logging.StreamHandler()
    
    handlers = [file_handler, stream_handler]
    logger.handlers = handlers
    
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
