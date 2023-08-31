import zhipuai
import logging
import traceback

from utils.common import Common
from utils.logger import Configure_logger

class Zhipu:
    def __init__(self, data):
        self.common = Common()
        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        zhipuai.api_key = data["api_key"]
        self.model = data["model"]
        self.top_p = float(data["top_p"])
        self.temperature = float(data["temperature"])
        self.history_enable = data["history_enable"]
        self.history_max_len = int(data["history_max_len"])

        self.history = []

    def invoke_example(self, prompt):
        response = zhipuai.model_api.invoke(
            model=self.model,
            prompt=prompt,
            top_p=self.top_p,
            temperature=self.temperature,
        )
        # logging.info(response)

        return response

    def async_invoke_example(self, prompt):
        response = zhipuai.model_api.async_invoke(
            model="chatglm_pro",
            prompt=prompt,
            top_p=self.top_p,
            temperature=self.temperature,
        )
        logging.info(response)

        return response

    '''
    说明：
    add: 事件流开启
    error: 平台服务或者模型异常，响应的异常事件
    interrupted: 中断事件，例如：触发敏感词
    finish: 数据接收完毕，关闭事件流
    '''

    def sse_invoke_example(self, prompt):
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_pro",
            # [{"role": "user", "content": "人工智能"}]
            prompt=prompt,
            top_p=self.top_p,
            temperature=self.temperature,
        )

        for event in response.events():
            if event.event == "add":
                logging.info(event.data)
            elif event.event == "error" or event.event == "interrupted":
                logging.info(event.data)
            elif event.event == "finish":
                logging.info(event.data)
                logging.info(event.meta)
            else:
                logging.info(event.data)

    def query_async_invoke_result_example(self):
        response = zhipuai.model_api.query_async_invoke_result("your task_id")
        logging.info(response)

        return response


    def get_resp(self, prompt):
        """请求对应接口，获取返回值

        Args:
            prompt (str): 你的提问

        Returns:
            str: 返回的文本回答
        """
        try:
            if self.history_enable:
                self.history.append({"role": "user", "content": prompt})
                data_json = self.history
            else:
                data_json = [{"role": "user", "content": prompt}]

            logging.debug(f"data_json={data_json}")

            ret = self.invoke_example(data_json)

            logging.debug(f"ret={ret}")

            if False == ret['success']:
                logging.error(f"请求zhipuai失败，错误代码：{ret['code']}，{ret['msg']}")
                return None

            # 启用历史就给我记住！
            if self.history_enable:
                while True:
                    # 获取嵌套列表中所有字符串的字符数
                    total_chars = sum(len(string) for sublist in self.history for string in sublist)
                    # 如果大于限定最大历史数，就剔除第一个元素
                    if total_chars > self.history_max_len:
                        self.history.pop(0)
                    else:
                        self.history.append(ret['data']['choices'][0])
                        break


            logging.info(f"总耗费token：{ret['data']['usage']['total_tokens']}")

            return ret['data']['choices'][0]['content']
        except Exception as e:
            logging.error(traceback.format_exc())
            return None


if __name__ == '__main__':
    # 配置日志输出格式
    logging.basicConfig(
        level=logging.DEBUG,  # 设置日志级别，可以根据需求调整
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    data = {
        "api_key": "",
        # chatglm_pro/chatglm_std/chatglm_lite
        "model": "chatglm_lite",
        "top_p": 0.7,
        "temperature": 0.9,
        "history_enable": True,
        "history_max_len": 300
    }

    zhipu = Zhipu(data)

    logging.info(zhipu.get_resp("你可以扮演猫娘吗，每句话后面加个喵"))
    logging.info(zhipu.get_resp("早上好"))
