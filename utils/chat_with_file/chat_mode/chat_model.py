# -*- coding: UTF-8 -*-
"""
@Project : PyCharm 
@File    : chat_model.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/6/28 17:09
@Description : 
"""
from utils.gpt_model.gpt import GPT_MODEL


class Chat_model:
    # 通用配置信息
    chat_mode = None
    data_path = None
    separator = "\n"
    chunk_size = 100
    chunk_overlap = 50

    # openai 设置
    openai_api_key = None
    openai_model_name = "gpt-3.5-turbo-0301"
    chain_type = "stuff"
    show_token_cost = False

    # 本地向量数据库配置
    local_vector_embedding_model = "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco"
    local_max_query = 3

    # prompt配置
    question_prompt = None

    def __init__(self, data):
        # 通用配置信息
        self.chat_mode = data["chat_mode"]
        self.data_path = data["data_path"]
        self.separator = data["separator"]
        self.chunk_size = data["chunk_size"]
        self.chunk_overlap = data["chunk_overlap"]

        # openai 设置
        self.openai_api_key = GPT_MODEL.get_openai_key()
        self.openai_model_name = GPT_MODEL.get_openai_model_name()
        self.chain_type = data["chain_type"]
        self.show_token_cost = data["show_token_cost"]

        # 本地向量数据库配置
        self.local_vector_embedding_model = data["local_vector_embedding_model"]
        self.local_max_query = data["local_max_query"]

        # prompt配置
        self.question_prompt = data["question_prompt"]

    def get_model_resp(self, question=""):
        pass
