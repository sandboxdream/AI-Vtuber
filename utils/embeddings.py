# -*- coding: UTF-8 -*-
"""
@Project : AI-Vtuber
@File    : langchain_pdf_local.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/06/17 下午 4:44
@Description : 本地向量数据库模型设置
"""

from langchain.embeddings import HuggingFaceEmbeddings


"""
    模型1："sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco"
"""
DEFAULT_MODEL_NAME = "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco"
DEFAULT_MODEL_KWARGS = {'device': 'cpu'}
DEFAULT_ENCODE_KWARGS = {'normalize_embeddings': False}
hf_embeddings = HuggingFaceEmbeddings(
    model_name=DEFAULT_MODEL_NAME,
    model_kwargs=DEFAULT_MODEL_KWARGS,
    encode_kwargs=DEFAULT_ENCODE_KWARGS
)


"""
    模型列表
"""
EMBEDDINGS_MAPPING = {DEFAULT_MODEL_NAME: hf_embeddings}