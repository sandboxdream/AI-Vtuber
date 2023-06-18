# -*- coding: UTF-8 -*-
"""
@Project : AI-Vtuber
@File    : langchain_pdf_local.py
@Author  : HildaM
@Email   : Hilda_quan@163.com
@Date    : 2023/06/17 下午 4:44
@Description : 本地向量数据库配置
"""


import json
from langchain.vectorstores import FAISS
import os
from tqdm.auto import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from utils.embeddings import EMBEDDINGS_MAPPING
import tiktoken
import zipfile
import pickle

tokenizer_name = tiktoken.encoding_for_model('gpt-4')
tokenizer = tiktoken.get_encoding(tokenizer_name.name)


#######################################################################################################################
# Files handler
#######################################################################################################################
def check_existence(path):
    return os.path.isfile(path) or os.path.isdir(path)


def list_files(directory, ext=".pdf"):
    # List all files in the directory
    files_in_directory = os.listdir(directory)
    # Filter the list to only include PDF files
    files_list = [file for file in files_in_directory if file.endswith(ext)]
    return files_list


def list_pdf_files(directory):
    # List all files in the directory
    files_in_directory = os.listdir(directory)
    # Filter the list to only include PDF files
    pdf_files = [file for file in files_in_directory if file.endswith(".pdf")]
    return pdf_files


def tiktoken_len(text):
    # evaluate how many tokens for the given text
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)


def get_chunks(docs, chunk_size=500, chunk_overlap=20, length_function=tiktoken_len):
    # docs should be the output of `loader.load()`
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                                   chunk_overlap=chunk_overlap,
                                                   length_function=length_function,
                                                   separators=["\n\n", "\n", " ", ""])
    chunks = []
    for idx, page in enumerate(tqdm(docs)):
        source = page.metadata.get('source')
        content = page.page_content
        if len(content) > 50:
            texts = text_splitter.split_text(content)
            chunks.extend([str({'content': texts[i], 'chunk': i, 'source': os.path.basename(source)}) for i in
                           range(len(texts))])
    return chunks


#######################################################################################################################
# Create FAISS object
#######################################################################################################################

"""
    支持的模型：
        distilbert-dot-tas_b-b256-msmarco
"""


def create_faiss_index_from_zip(path_to_zip_file, embeddings=None, pdf_loader=None,
                                chunk_size=500, chunk_overlap=20,
                                project_name="Please_Delete_This_File_After_Running"):
    # 存储的文件格式
    # structure: project_name
    #               - source data
    #               - embeddings
    #               - faiss_index
    if isinstance(embeddings, str):
        import copy
        embeddings_str = copy.deepcopy(embeddings)
    else:
        embeddings_str = "distilbert-dot-tas_b-b256-msmarco"  # 默认模型

    # 选择模型
    if embeddings is None:
        embeddings = EMBEDDINGS_MAPPING["distilbert-dot-tas_b-b256-msmarco"]
    elif isinstance(embeddings, str):
        embeddings = EMBEDDINGS_MAPPING[embeddings]

    # 创建存储向量数据库的目录
    store_path = os.getcwd() + "/data/vector_base/"
    if not os.path.exists(store_path + project_name):
        os.makedirs(store_path)
        project_path = os.path.join(store_path, project_name)
        source_data = os.path.join(project_path, "source_data")
        embeddings_data = os.path.join(project_path, "embeddings")
        index_data = os.path.join(project_path, "faiss_index")
        os.makedirs(source_data)  # ./project/source_data
        os.makedirs(embeddings_data)  # ./project/embeddings
        os.makedirs(index_data)  # ./project/faiss_index
    else:
        raise ValueError(f"向量数据库文件夹重名，请删除重名文件夹后再启动。")

    # 解压数据包
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        # extract everything to "source_data"
        zip_ref.extractall(source_data)

    # 组装数据库元信息
    db_meta = {"project_name": project_name,
               "pdf_loader": pdf_loader.__name__, "chunk_size": chunk_size,
               "chunk_overlap": chunk_overlap,
               "embedding_model": embeddings_str,
               "files": os.listdir(source_data),
               "source_path": source_data}
    with open(os.path.join(project_path, "db_meta.json"), "w", encoding="utf-8") as f:
        # save db_meta.json to folder
        json.dump(db_meta, f)

    # 处理不同的文件
    all_docs = []
    for ext in [".txt", ".tex", ".md", ".pdf"]:
        if ext in [".txt", ".tex", ".md"]:
            loader = DirectoryLoader(source_data, glob=f"**/*{ext}", loader_cls=TextLoader,
                                     loader_kwargs={'autodetect_encoding': True})
        elif ext in [".pdf"]:
            loader = DirectoryLoader(source_data, glob=f"**/*{ext}", loader_cls=pdf_loader)
        else:
            continue
        docs = loader.load()
        all_docs = all_docs + docs

    # 数据分片
    chunks = get_chunks(all_docs, chunk_size, chunk_overlap)

    # 向量数据
    text_embeddings = embeddings.embed_documents(chunks)
    text_embedding_pairs = list(zip(chunks, text_embeddings))

    # 向量数据保存位置
    embeddings_save_to = os.path.join(embeddings_data, 'text_embedding_pairs.pickle')

    # 保存数据
    with open(embeddings_save_to, 'wb') as handle:
        pickle.dump(text_embedding_pairs, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # 将向量数据保存进FAISS中
    db = FAISS.from_embeddings(text_embedding_pairs, embeddings)
    db.save_local(index_data)

    return db


def find_file(file_name, directory):
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            return os.path.join(root, file_name)
    return None  # If the file was not found


def find_file_dir(file_name, directory):
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            return root  # return the directory instead of the full path
    return None  # If the file was not found


# 加载本地数据
def load_faiss_index_from_zip(path_to_zip_file):
    # Extract the zip file. Read the db_meta
    # base_name = os.path.basename(path_to_zip_file)
    path_to_extract = os.path.join(os.getcwd())
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(path_to_extract)

    db_meta_json = find_file("db_meta.json", path_to_extract)
    if db_meta_json is not None:
        with open(db_meta_json, "r", encoding="utf-8") as f:
            db_meta_dict = json.load(f)
    else:
        raise ValueError("Cannot find `db_meta.json` in the .zip file. ")

    try:
        embeddings = EMBEDDINGS_MAPPING[db_meta_dict["embedding_model"]]
    except:
        from langchain.embeddings.openai import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    # locate index.faiss
    index_path = find_file_dir("index.faiss", path_to_extract)
    if index_path is not None:
        db = FAISS.load_local(index_path, embeddings)
        return db
    else:
        raise ValueError("Failed to find `index.faiss` in the .zip file.")


# 测试代码
if __name__ == "__main__":
    from langchain.document_loaders import PyPDFLoader
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.embeddings import HuggingFaceEmbeddings

    zip_file_path = "data/伊卡洛斯百度百科.zip"
    model_name = "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs)
    create_faiss_index_from_zip(path_to_zip_file=zip_file_path, pdf_loader=PyPDFLoader, embeddings=embeddings)

    db = load_faiss_index_from_zip(zip_file_path)
