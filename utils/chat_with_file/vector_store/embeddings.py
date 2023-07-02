# -*- coding: UTF-8 -*-
"""
@Project : AI-Vtuber
@File    : claude_model.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/06/17 下午 4:44
@Description : 本地向量数据库模型设置
"""

from langchain.embeddings import HuggingFaceEmbeddings
import os


# 项目根路径
TEC2VEC_MODELS_PATH = os.getcwd() + "\\" + "data" + "\\" + "text2vec_models" "\\"

# 默认模型
DEFAULT_MODEL_NAME = "sebastian-hofstaetter_distilbert-dot-tas_b-b256-msmarco"


def get_default_model():
    return HuggingFaceEmbeddings(model_name=TEC2VEC_MODELS_PATH + DEFAULT_MODEL_NAME)


def get_text2vec_model(model_name):
    """
        0. 判空。若为空，加载内置模型
        1. 先判断项目data/tec2vec_models目录中是否存在模型
        2. 存在则直接加载
        3. 不存在，则从Huggingface中下载到本地，保存在系统cache中
    """
    if model_name is None:
        return HuggingFaceEmbeddings(model_name=TEC2VEC_MODELS_PATH + DEFAULT_MODEL_NAME)

    model_path = TEC2VEC_MODELS_PATH + model_name
    if os.path.exists(model_path):
        return HuggingFaceEmbeddings(model_name=model_path)
    else:
        return HuggingFaceEmbeddings(model_name=model_name)
