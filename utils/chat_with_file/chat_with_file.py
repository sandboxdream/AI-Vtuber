# -*- coding: UTF-8 -*-
"""
@Project : AI-Vtuber
@File    : chat_with_file.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/6/28 16:24
@Description : 
"""
from langchain.document_loaders import PyPDFLoader

from utils.chat_with_file.chat_mode.claude_model import Claude_mode
from utils.chat_with_file.chat_mode.openai_model import Openai_mode
from utils.common import Common
from utils.logger import Configure_logger


class Chat_with_file:
    chat_model = None

    def __init__(self, data, chat_type="chat_with_file"):
        self.common = Common()
        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        # 选择模式
        match data["chat_mode"]:
            case "claude":
                self.chat_model = Claude_mode(data)
            case "openai_gpt":
                self.chat_model = Openai_mode(data)
            case "openai_vector_search":
                self.chat_model = Openai_mode(data)

    def get_model_resp(self, question):
        return self.chat_model.get_model_resp(question)
