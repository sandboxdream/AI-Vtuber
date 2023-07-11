from .common import Common
from .logger import Configure_logger
from .config import Config


class Video:
    def __init__(self, config_path):  
        self.config = Config(config_path)
        self.common = Common()

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)


    # 音频转视频 排队合成
    def wav2video(self, ):
        pass


    
