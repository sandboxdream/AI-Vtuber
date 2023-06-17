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
model_name = "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
hf_embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

EMBEDDINGS_MAPPING = {"distilbert-dot-tas_b-b256-msmarco": hf_embeddings}