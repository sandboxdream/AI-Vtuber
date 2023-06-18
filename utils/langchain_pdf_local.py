# -*- coding: UTF-8 -*-
"""
@Project : AI-Vtuber 
@File    : langchain_pdf_local.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/06/17 下午 4:44 
@Description : 本地化向量数据库，实现langchain_pdf
"""


import uuid
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings

from utils.claude import Claude
from utils.faiss_handler import load_faiss_index_from_zip, create_faiss_index_from_zip
from utils.my_handle import My_handle


# 由于similarity_search返回的数据不是标准的json格式，不能用过python格式化，所以只能用字符串操作获取数据
# 返回的数据很标准，可以很方便获取content信息
def get_content(data: str):
    prefix = "{'content': "
    surfix = ", 'chunk'"

    start = data.find(prefix)
    end = data.find(surfix)
    return data[start:end]


class Langchain_pdf_local:
    langchain_pdf_bot_user_id = None
    langchain_pdf_slack_user_token = None
    langchain_pdf_data_path = None
    langchain_pdf_separator = "\n"
    langchain_pdf_chunk_size = 100
    langchain_pdf_chunk_overlap = 50
    langchain_pdf_embedding_model = "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco"
    langchain_pdf_chain_type = "stuff"
    langchain_pdf_show_cost = None
    langchain_pdf_question_prompt = ""
    langchain_pdf_max_query = 0
    docsearch = None
    chain = None
    pdf_loader = PyPDFLoader
    local_db = None
    claude = None

    def __init__(self, data, chat_type="langchain_pdf_local"):
        self.langchain_pdf_bot_user_id = data["bot_user_id"]
        self.langchain_pdf_slack_user_token = data["slack_user_token"]
        self.langchain_pdf_data_path = data["data_path"]
        self.langchain_pdf_separator = data["separator"]
        self.langchain_pdf_chunk_size = data["chunk_size"]
        self.langchain_pdf_chunk_overlap = data["chunk_overlap"]
        self.langchain_pdf_embedding_model = data["embedding_model"]
        self.langchain_pdf_chain_type = data["chain_type"]
        self.langchain_pdf_show_cost = data["show_cost"]
        self.langchain_pdf_question_prompt = data["question_prompt"]
        self.langchain_pdf_max_query = data["max_query"]

        print(f"pdf文件路径：{self.langchain_pdf_data_path}")

        # 加载pdf并生成向量数据库
        self.load_zip_as_db(self.langchain_pdf_data_path, self.pdf_loader,
                            self.langchain_pdf_embedding_model, self.langchain_pdf_chunk_size,
                            self.langchain_pdf_chunk_overlap)
        # 初始化claude客户端
        self.claude = Claude(data)

    def load_zip_as_db(self, zip_file,
                       pdf_loader,
                       model_name,
                       chunk_size=300,
                       chunk_overlap=20):
        if chunk_size <= chunk_overlap:
            print("ERROR: chunk_size小于chunk_overlap. 创建失败.")
            return
        if zip_file is None:
            print("ERROR: 文件为空. 创建失败.")
            return

        project_name = uuid.uuid4().hex

        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        self.local_db = create_faiss_index_from_zip(
            path_to_zip_file=zip_file,
            embeddings=embeddings,
            pdf_loader=pdf_loader,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            project_name=project_name
        )

        print("成功创建向量知识库!")

    # 调用本地向量数据库，获取关联信息
    def get_local_database_data(self, message):
        print(f"开始从本地向量数据库中查询有关”{message}“的信息........")

        contents = []
        docs = self.local_db.similarity_search(message, k=self.langchain_pdf_max_query)
        for i in range(self.langchain_pdf_max_query):
            # 预处理分块
            content = docs[i].page_content.replace('\n', ' ')
            print(f"No.{i} 相关联信息: {content}")
            data = get_content(content)
            # 更新contents
            contents.append(data)

        print("从本地向量数据库查询到的相关信息: {}".format(contents))
        if len(contents) == 0 or contents is None:
            return
        related_data = "\n---\n".join(contents) + "\n---\n"
        return related_data

    def load_local_db(self, zip_file):
        if zip_file is None:
            return "文件为空. 创建失败.", None
        self.local_db = load_faiss_index_from_zip(zip_file)

        print("成功读取知识库")

    def get_langchain_pdf_local_resp(self, chat_type="langchain_pdf", question=""):
        if self.local_db is None:
            self.load_local_db(self.langchain_pdf_data_path)

        related_data = self.get_local_database_data(question)
        if related_data is None or len(related_data) <= 0:
            content = question
        else:
            content = related_data + "\n" + self.langchain_pdf_question_prompt + " question: " + question

        resp = self.claude.get_claude_resp(content)
        return resp


if __name__ == '__main__':
    my_handle = My_handle("config.json")
    if my_handle is None:
        print("程序初始化失败！")
        exit(0)
