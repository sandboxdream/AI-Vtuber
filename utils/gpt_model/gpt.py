# -*- coding: UTF-8 -*-
"""
@Project : AI-Vtuber 
@File    : gpt.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/06/23 下午 7:47 
@Description :  统一模型层抽象
"""
import logging

from utils.gpt_model.chatglm import Chatglm
from utils.gpt_model.chatgpt import Chatgpt
from utils.gpt_model.claude import Claude


class GPT_Model:
    # 模型配置信息
    openai_key = None
    chatgpt = None
    claude = None
    chatglm = None

    def set_model_config(self, model_name, *config):
        if model_name == "chatgpt":
            self.openai_key = config[0]
            self.chatgpt = Chatgpt(self.openai_key, config[1])
        elif model_name == "claude":
            self.claude = Claude(config[0])
        elif model_name == "chatglm":
            self.chatglm = Chatglm(config[0])

    def get(self, name):
        logging.info("GPT_MODEL: 进入get方法")
        match name:
            case "chatgpt":
                return self.chatgpt
            case "claude":
                return self.claude
            case "chatglm":
                return self.chatglm
            case _:
                logging.error(f"{name} 该模型不支持")
                return


# 全局变量
GPT_MODEL = GPT_Model()
