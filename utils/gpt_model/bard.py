from bardapi import Bard
import requests
import logging
import traceback

from utils.common import Common
from utils.logger import Configure_logger

class Bard_api(Common):
    def __init__(self, data):
        self.common = Common()
        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        """
        访问 https://bard.google.com/
        F12 打开开发者工具
        会话：应用程序 → Cookie → 复制 Cookie 中 __Secure-1PSID 对应的值。
        """
        self.token = data["token"]

        self.session = requests.Session()
        self.session.headers = {
            "Host": "bard.google.com",
            "X-Same-Domain": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://bard.google.com",
            "Referer": "https://bard.google.com/",
        }
        self.session.cookies.set("__Secure-1PSID", self.token) 


    # 调用接口，获取返回内容
    def get_resp(self, prompt):
        try:
            bard = Bard(token=self.token, session=self.session, timeout=30)
            resp_content = bard.get_answer(prompt)['content'].replace("\\n", "")

            return resp_content
        except Exception as e:
            logging.error(traceback.format_exc())
            return None
