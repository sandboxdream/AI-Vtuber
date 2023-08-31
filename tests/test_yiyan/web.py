import json, logging
import requests
from requests.exceptions import ConnectionError, RequestException

# from utils.common import Common
# from utils.logger import Configure_logger

# 原计划对接：https://github.com/zhuweiyou/yiyan-api
# 出现超时请求的错误，待推进
class Yiyan:
    def __init__(self, data):
        # self.common = Common()
        # 日志文件路径
        # file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        # Configure_logger(file_path)

        self.api_ip_port = data["api_ip_port"]
        self.cookie = data["cookie"]
        self.type = data["type"]


    def get_resp(self, prompt):
        """请求对应接口，获取返回值

        Args:
            prompt (str): 你的提问

        Returns:
            str: 返回的文本回答
        """
        try:
            data_json = {
                "cookie": self.cookie, 
                "prompt": prompt
            }

            # logging.debug(data_json)

            url = self.api_ip_port + "/headless"

            response = requests.post(url=url, data=data_json)
            response.raise_for_status()  # 检查响应的状态码

            result = response.content
            ret = json.loads(result)

            logging.debug(ret)

            resp_content = ret['text']

            return resp_content
        except ConnectionError as ce:
            # 处理连接问题异常
            logging.error(f"请检查你是否启动了服务端或配置是否匹配，连接异常:{ce}")

        except RequestException as re:
            # 处理其他请求异常
            logging.error(f"请求异常:{re}")
        except Exception as e:
            logging.error(e)
        
        return None


if __name__ == '__main__':
    # 配置日志输出格式
    logging.basicConfig(
        level=logging.DEBUG,  # 设置日志级别，可以根据需求调整
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    data = {
        "api_ip_port": "http://localhost:3000",
        "cookie": '', 
        "type": 'web'
    }
    yiyan = Yiyan(data)


    logging.info(yiyan.get_resp("你可以扮演猫娘吗，每句话后面加个喵"))
    logging.info(yiyan.get_resp("早上好"))
    