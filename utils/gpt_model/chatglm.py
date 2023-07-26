import json, logging
import requests

from utils.common import Common
from utils.logger import Configure_logger

class Chatglm:
    def __init__(self, data):
        self.common = Common()
        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.api_ip_port = data["api_ip_port"]
        self.max_length = data["max_length"]
        self.top_p = data["top_p"]
        self.temperature = data["temperature"]
        self.history_enable = data["history_enable"]

        self.history = []


    # 调用chatglm接口，获取返回内容
    def get_chatglm_resp(self, prompt):
        data_json = {
            "prompt": prompt, 
            "history": self.history,
            "max_length": self.max_length,
            "top_p": self.top_p,
            "temperature": self.temperature
        }

        try:
            response = requests.post(url=self.api_ip_port, json=data_json)
            response.raise_for_status()  # 检查响应的状态码

            result = response.content
            ret = json.loads(result)

            resp_content = ret['response']

            # 启用历史就给我记住！
            if self.history_enable:
                self.history = ret['history']

            return resp_content
        except Exception as e:
            logging.info(e)
            return None