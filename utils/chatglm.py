import json
import requests


class Chatglm:
    api_ip_port = "http://127.0.0.1:8000"
    max_length = 2048
    top_p = 0.7
    temperature = 0.95

    def __init__(self, data):
        self.api_ip_port = data["api_ip_port"]
        self.max_length = data["max_length"]
        self.top_p = data["top_p"]
        self.temperature = data["temperature"]


    # 调用chatglm接口，获取返回内容
    def get_chatglm_resp(self, prompt, history=[]):
        data_json = {
            "prompt": prompt, 
            "history": history,
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

            return resp_content
        except Exception as e:
            print(e)
            return None