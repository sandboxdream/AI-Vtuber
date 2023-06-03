import _thread
import binascii
import gzip
import json
import logging
import re
import time
import requests
import websocket
import urllib
from protobuf_inspector.types import StandardParser
from google.protobuf import json_format
from dy_pb2 import PushFrame
from dy_pb2 import Response
from dy_pb2 import MatchAgainstScoreMessage
from dy_pb2 import LikeMessage
from dy_pb2 import MemberMessage
from dy_pb2 import GiftMessage
from dy_pb2 import ChatMessage
from dy_pb2 import SocialMessage
from dy_pb2 import RoomUserSeqMessage
from dy_pb2 import UpdateFanTicketMessage
from dy_pb2 import CommonTextMessage

# 导入所需的库
import json, re, os, threading
import subprocess
import traceback
from copy import deepcopy
from datetime import datetime
from datetime import timedelta
from datetime import timezone

# import aiohttp, asyncio
import langid

import pygame

from profanity import profanity


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
# 不想看那么多日志信息，可以把日志等级提一提
logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)

liveRoomId = None
ttwid = None
roomStore = None
liveRoomTitle = None

# proxy = {
#     "http": "http://127.0.0.1:10809",
#     "https": "http://127.0.0.1:10809"
# }

proxy = None

# 读取配置文件信息
with open("config.json", "r", encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)

try:
    # 设置会话初始值
    session_config = {'msg': [{"role": "system", "content": config_data['chatgpt']['preset']}]}
    sessions = {}
    current_key_index = 0

    # 抖音直播间号
    room_id = config_data["room_display_id"]

    before_promet = config_data["before_promet"]
    after_promet = config_data["after_promet"]

    # 敏感词数据路径
    badwords_path = config_data["badwords_path"]

    # 最大阅读单词数
    max_len = int(config_data["max_len"])
    # 最大阅读字符数
    max_char_len = int(config_data["max_char_len"])

    chat_type = config_data["chat_type"]

    need_lang = config_data["need_lang"]

    # claude
    slack_user_token = config_data["claude"]["slack_user_token"]
    bot_user_id = config_data["claude"]["bot_user_id"]

    # chatterbot
    chatterbot_name = config_data["chatterbot"]["name"]
    chatterbot_db_path = config_data["chatterbot"]["db_path"]

    # langchain_pdf
    langchain_pdf_openai_api_key = config_data["langchain_pdf"]["openai_api_key"]
    langchain_pdf_data_path = config_data["langchain_pdf"]["data_path"]
    langchain_pdf_separator = config_data["langchain_pdf"]["separator"]
    langchain_pdf_chunk_size = config_data["langchain_pdf"]["chunk_size"]
    langchain_pdf_chunk_overlap = config_data["langchain_pdf"]["chunk_overlap"]
    langchain_pdf_model_name = config_data["langchain_pdf"]["model_name"]
    langchain_pdf_chain_type = config_data["langchain_pdf"]["chain_type"]
    langchain_pdf_show_cost = config_data["langchain_pdf"]["chain_type"]

    # 音频合成使用技术
    audio_synthesis_type = config_data["audio_synthesis_type"]

    # vits配置文件路径(注意路径转义问题)
    vits_config_path = config_data["vits"]["config_path"]
    # api的ip和端口，注意书写格式
    vits_api_ip_port = config_data["vits"]["api_ip_port"]
    character = config_data["vits"]["character"]
    # character = "妮姆芙"
    language = "日语"
    text = "こんにちわ。"
    speed = 1
    speakers = None

    # edge-tts配置
    tts_voice = config_data["edge-tts"]["voice"]

    # elevenlabs配置
    elevenlabs_api_key = config_data["elevenlabs"]["api_key"]
    elevenlabs_voice = config_data["elevenlabs"]["voice"]
    elevenlabs_model = config_data["elevenlabs"]["model"]

    print("配置文件加载成功。")
except Exception as e:
    print(e)
    exit(0)


# vits模式下加载配置
if audio_synthesis_type == "vits":
    try:
        with open(vits_config_path, "r", encoding="utf-8") as file:
            vits_data = json.load(file)
        
        # 加载说话人配置
        speakers = vits_data["speakers"]
    except Exception as e:
        print('加载配置文件失败，请进行修复')
        exit(0)
elif audio_synthesis_type == "elevenlabs":
    from elevenlabs import generate, play, set_api_key


# 获取北京时间
def get_bj_time(type=0):
    if type == 0:
        """
        获取北京时间
        :return: 当前北京时间，格式为 '%Y-%m-%d %H:%M:%S'
        """
        utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
        SHA_TZ = timezone(
            timedelta(hours=8),
            name='Asia/Shanghai',
        )
        beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
        fmt = '%Y-%m-%d %H:%M:%S'
        now_fmt = beijing_now.strftime(fmt)
        return now_fmt
    elif type == 1:
        now = datetime.now()  # 获取当前时间
        year = now.year  # 获取当前年份
        month = now.month  # 获取当前月份
        day = now.day  # 获取当前日期

        return str(year) + "-" + str(month) + "-" + str(day)
    elif type == 2:
        now = time.localtime()  # 获取当前时间

        # hour = now.tm_hour   # 获取当前小时
        # minute = now.tm_min  # 获取当前分钟 
        second = now.tm_sec  # 获取当前秒数

        return str(second)


# 日志文件路径
log_file_path = "./log/log-" + get_bj_time(1) + ".txt"
if os.path.isfile(log_file_path):
    print(f'{log_file_path} 日志文件已存在，跳过')
else:
    with open(log_file_path, 'w') as f:
        f.write('')
        print(f'{log_file_path} 日志文件已创建')


# 删除多余单词
def remove_extra_words(text="", max_len=30, max_char_len=50):
    words = text.split()
    if len(words) > max_len:
        words = words[:max_len]  # 列表切片，保留前30个单词
        text = ' '.join(words) + '...'  # 使用join()函数将单词列表重新组合为字符串，并在末尾添加省略号
    return text[:max_char_len]


# 本地敏感词检测 传入敏感词库文件路径和待检查的文本
def check_sensitive_words(file_path, text):
    with open(file_path, 'r', encoding='utf-8') as file:
        sensitive_words = [line.strip() for line in file.readlines()]

    for word in sensitive_words:
        if word in text:
            return True

    return False


# 链接检测
def is_url_check(text):
    url_pattern = re.compile(r'(?i)((?:(?:https?|ftp):\/\/)?[^\s/$.?#]+\.[^\s>]+)')

    if url_pattern.search(text):
        return True
    else:
        return False


# 语言检测
def lang_check(text, need="none"):
    # 语言检测 一个是语言，一个是概率
    language, score = langid.classify(text)

    if need == "none":
        return language
    else:
        if language != need:
            return None
        else:
            return language


if chat_type == "claude":
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError

    client = WebClient(token=slack_user_token)

    ### claude
    def send_message(channel, text):
        try:
            return client.chat_postMessage(channel=channel, text=text)
        except SlackApiError as e:
            print(f"Error sending message: {e}")
            return None

    def fetch_messages(channel, last_message_timestamp):
        response = client.conversations_history(channel=channel, oldest=last_message_timestamp)
        return [msg['text'] for msg in response['messages'] if msg['user'] == bot_user_id]

    def get_new_messages(channel, last_message_timestamp):
        timeout = 60  # 超时时间设置为60秒
        start_time = time.time()

        while True:
            messages = fetch_messages(channel, last_message_timestamp)
            if messages and not messages[-1].endswith('Typing…_'):
                return messages[-1]
            if time.time() - start_time > timeout:
                return None
            
            time.sleep(5)

    def find_direct_message_channel(user_id):
        try:
            response = client.conversations_open(users=user_id)
            return response['channel']['id']
        except SlackApiError as e:
            print(f"Error opening DM channel: {e}")
            return None

    # 获取claude返回内容
    def get_claude_resp(text):
        response = send_message(dm_channel_id, text)
        if response:
            last_message_timestamp = response['ts']
        else:
            return None

        new_message = get_new_messages(dm_channel_id, last_message_timestamp)
        if new_message is not None:
            return new_message
        return None


    dm_channel_id = find_direct_message_channel(bot_user_id)
    if not dm_channel_id:
        print("Could not find DM channel with the bot.")
        exit(0)

    last_message_timestamp = None
elif chat_type == "gpt":
    import openai

    # 配置 OpenAI API 和 Bilibili 直播间 ID
    openai.api_base = config_data["openai"]["api"]  # https://chat-gpt.aurorax.cloud/v1 https://api.openai.com/v1

    # chatgpt相关
    def chat(msg, sessionid):
        """
        ChatGPT 对话函数
        :param msg: 用户输入的消息
        :param sessionid: 当前会话 ID
        :return: ChatGPT 返回的回复内容
        """
        try:
            # 获取当前会话
            session = get_chat_session(sessionid)

            # 将用户输入的消息添加到会话中
            session['msg'].append({"role": "user", "content": msg})

            # 添加当前时间到会话中
            session['msg'][1] = {"role": "system", "content": "current time is:" + get_bj_time()}

            # 调用 ChatGPT 接口生成回复消息
            message = chat_with_gpt(session['msg'])

            # 如果返回的消息包含最大上下文长度限制，则删除超长上下文并重试
            if message.__contains__("This model's maximum context length is 4096 token"):
                del session['msg'][2:3]
                del session['msg'][len(session['msg']) - 1:len(session['msg'])]
                message = chat(msg, sessionid)

            # 将 ChatGPT 返回的回复消息添加到会话中
            session['msg'].append({"role": "assistant", "content": message})

            # 输出会话 ID 和 ChatGPT 返回的回复消息
            print("会话ID: " + str(sessionid))
            print("ChatGPT返回内容: ")
            print(message)

            # 返回 ChatGPT 返回的回复消息
            return message

        # 捕获异常并打印堆栈跟踪信息
        except Exception as error:
            traceback.print_exc()
            return str('异常: ' + str(error))


    def get_chat_session(sessionid):
        """
        获取指定 ID 的会话，如果不存在则创建一个新的会话
        :param sessionid: 会话 ID
        :return: 指定 ID 的会话
        """
        sessionid = str(sessionid)
        if sessionid not in sessions:
            config = deepcopy(session_config)
            config['id'] = sessionid
            config['msg'].append({"role": "system", "content": "current time is:" + get_bj_time()})
            sessions[sessionid] = config
        return sessions[sessionid]


    def chat_with_gpt(messages):
        """
        使用 ChatGPT 接口生成回复消息
        :param messages: 上下文消息列表
        :return: ChatGPT 返回的回复消息
        """
        global current_key_index
        max_length = len(config_data['openai']['api_key']) - 1

        try:
            if not config_data['openai']['api_key']:
                return "请设置Api Key"
            else:
                # 判断是否所有 API key 均已达到速率限制
                if current_key_index > max_length:
                    current_key_index = 0
                    return "全部Key均已达到速率限制,请等待一分钟后再尝试"
                openai.api_key = config_data['openai']['api_key'][current_key_index]

            # 调用 ChatGPT 接口生成回复消息
            resp = openai.ChatCompletion.create(
                model=config_data['chatgpt']['model'],
                messages=messages
            )
            resp = resp['choices'][0]['message']['content']

        # 处理 OpenAIError 异常
        except openai.OpenAIError as e:
            if str(e).__contains__("Rate limit reached for default-gpt-3.5-turbo") and current_key_index <= max_length:
                current_key_index = current_key_index + 1
                print("速率限制，尝试切换key")
                return chat_with_gpt(messages)
            elif str(e).__contains__(
                    "Your access was terminated due to violation of our policies") and current_key_index <= max_length:
                print("请及时确认该Key: " + str(openai.api_key) + " 是否正常，若异常，请移除")

                # 判断是否所有 API key 均已尝试
                if current_key_index + 1 > max_length:
                    return str(e)
                else:
                    print("访问被阻止，尝试切换Key")
                    current_key_index = current_key_index + 1
                    return chat_with_gpt(messages)
            else:
                print('openai 接口报错: ' + str(e))
                resp = "openai 接口报错: " + str(e)

        return resp


    # 调用gpt接口，获取返回内容
    def get_gpt_resp(user_name, promet):
        # 获取当前用户的会话
        session = get_chat_session(str(user_name))
        # 调用 ChatGPT 接口生成回复消息
        resp_content = chat(promet, session)

        return resp_content

elif chat_type == "chatterbot":
    from chatterbot import ChatBot  # 导入聊天机器人库

    bot = ChatBot(
        chatterbot_name,  # 聊天机器人名字
        database_uri='sqlite:///' + chatterbot_name  # 数据库URI，数据库用于存储对话历史
    )
elif chat_type == "langchain_pdf" or chat_type == "langchain_pdf+gpt":
    from PyPDF2 import PdfReader
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.text_splitter import CharacterTextSplitter
    from langchain.vectorstores import ElasticVectorSearch, Pinecone, Weaviate, FAISS

    print(f"pdf文件路径：{langchain_pdf_data_path}")

    # 加载本地的pdf文件
    reader = PdfReader(langchain_pdf_data_path)

    # read data from the file and put them into a variable called raw_text
    # 读取数据存入raw_text
    raw_text = ''
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            raw_text += text

    # print(raw_text)

    print("文档前100个字符：" + raw_text[:100])

    # We need to split the text that we read into smaller chunks so that during information retreival we don't hit the token size limits. 
    # 我们需要将读取的文本分成更小的块，这样在信息检索过程中就不会达到令牌大小的限制。
    text_splitter = CharacterTextSplitter(
        # 拆分文本的分隔符
        separator = langchain_pdf_separator,
        # 每个文本块的最大字符数(文本块字符越多，消耗token越多，回复越详细)
        chunk_size = langchain_pdf_chunk_size,
        # 两个相邻文本块之间的重叠字符数
        # 这种重叠可以帮助保持文本的连贯性，特别是当文本被用于训练语言模型或其他需要上下文信息的机器学习模型时
        chunk_overlap  = langchain_pdf_chunk_overlap,
        # 用于计算文本块的长度
        # 在这里，长度函数是len，这意味着每个文本块的长度是其字符数。在某些情况下，你可能想要使用其他的长度函数。
        # 例如，如果你的文本是由词汇组成的，你可能想要使用一个函数，其计算文本块中的词汇数，而不是字符数。
        length_function = len,
    )
    texts = text_splitter.split_text(raw_text)

    print("共切分为" + str(len(texts)) + "块文本内容")

    # 创建了一个OpenAIEmbeddings实例，然后使用这个实例将一些文本转化为向量表示（嵌入）。
    # 然后，这些向量被加载到一个FAISS（Facebook AI Similarity Search）索引中，用于进行相似性搜索。
    # 这种索引允许你在大量向量中快速找到与给定向量最相似的向量。
    embeddings = OpenAIEmbeddings(openai_api_key=langchain_pdf_openai_api_key)
    docsearch = FAISS.from_texts(texts, embeddings)

    # 当用户输入一个查询时，这个系统首先会在本地文档集合中进行相似性搜索，寻找与查询最相关的文档。
    # 然后，它会把这些相关文档以及用户的查询作为输入，传递给语言模型。这个语言模型会基于这些输入生成一个答案。
    # 如果系统在本地文档集合中找不到任何与用户查询相关的文档，或者如果语言模型无法基于给定的输入生成一个有意义的答案，
    # 那么这个系统可能就无法回答用户的查询。
    if chat_type == "langchain_pdf+gpt":
        from langchain.chains.question_answering import load_qa_chain
        from langchain.llms import OpenAI
        from langchain.chat_models import ChatOpenAI
        from langchain.callbacks import get_openai_callback
        from langchain.prompts import PromptTemplate

        # 使用以下上下文来回答最后的问题。如果你不知道答案，就说你不知道或者你在文章中找不到答案，不要试图编造答案。
        prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know or you can't find the answer in the article, don't try to make up an answer.

        {context}

        Question: {question}
        Answer in Chinese:"""
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        # 创建一个询问-回答链（QA Chain），使用了一个自定义的提示模板
        chain = load_qa_chain(ChatOpenAI(model_name=langchain_pdf_model_name, openai_api_key=langchain_pdf_openai_api_key), \
            chain_type=langchain_pdf_chain_type, prompt=PROMPT)

        def query_func(str):
            with get_openai_callback() as cb:
                query = str
                # 将用户的查询进行相似性搜索，并使用QA链运行
                docs = docsearch.similarity_search(query)

                # 可以打印匹配的文档内容，看看
                # print(docs)

                res = chain.run(input_documents=docs, question=query)
                # print(f"Output: {res}")

                # 显示花费
                if langchain_pdf_show_cost:
                    # 相关消耗和费用
                    print(f"Total Tokens: {cb.total_tokens}")
                    print(f"Prompt Tokens: {cb.prompt_tokens}")
                    print(f"Completion Tokens: {cb.completion_tokens}")
                    print(f"Successful Requests: {cb.successful_requests}")
                    print(f"Total Cost (USD): ${cb.total_cost}")
                
                return res
# elif chat_type == "game":
    # from game1 import game1


# 请求VITS接口获取合成后的音频路径
def get_data(character="ikaros", language="日语", text="こんにちわ。", speed=1):
    # API地址
    API_URL = vits_api_ip_port + '/run/predict/'

    data_json = {
        "fn_index":0,
        "data":[
            "こんにちわ。",
            "ikaros",
            "日本語",
            1
        ],
        "session_hash":"mnqeianp9th"
    }

    if language == "中文" or language == "汉语":
        data_json["data"] = [text, character, "简体中文", speed]
    elif language == "英文" or language == "英语":
        data_json["data"] = [text, character, "English", speed]
    else:
        data_json["data"] = [text, character, "日本語", speed]

    try:
        response = requests.post(url=API_URL, json=data_json)
        response.raise_for_status()  # 检查响应的状态码

        result = response.content
        ret = json.loads(result)
        return ret
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url=API_URL, json=data_json) as response:
        #         result = await response.read()
        #         # print(result)
        #         ret = json.loads(result)
        # return ret
    except Exception as e:
        print(e)
        return None


# 播放音频
def my_play_voice(type, text):
    text = remove_extra_words(text, max_len, max_char_len)
    # print("裁剪后的合成文本:" + text)

    text = text.replace('\n', '。')

    if type == "vits":
        # 语言检测
        language = lang_check(text)

        # 自定义语言名称（需要匹配请求解析）
        language_name_dict = {"en": "英语", "zh": "中文", "jp": "日语"}  

        if language in language_name_dict:
            language = language_name_dict[language]
        else:
            language = "日语"  # 无法识别出语言代码时的默认值

        # print("language=" + language)

        try:
            # 调用接口合成语音
            data_json = get_data(character, language, text, speed)
            # print(data_json)
        except Exception as e:
            print(e)
            return

        voice_tmp_path = data_json["data"][1]["name"]

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(voice_tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(e)
    elif type == "edge-tts":
        voice_tmp_path = './out/' + get_bj_time(2) + '.mp3'
        # 过滤" '字符
        text = text.replace('"', '').replace("'", '').replace(" ", ',')
        # 使用 Edge TTS 生成回复消息的语音文件
        cmd = f'edge-tts --voice {tts_voice} --text "{text}" --write-media {voice_tmp_path}'
        subprocess.run(cmd, shell=True)

        # 会阻塞
        time.sleep(0.5)

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(voice_tmp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(e)
    elif type == "elevenlabs":
        try:
            # 如果配置了密钥就设置上0.0
            if elevenlabs_api_key != "":
                set_api_key(elevenlabs_api_key)

            audio = generate(
                text=text,
                voice=elevenlabs_voice,
                model=elevenlabs_model
            )

            play(audio)
        except Exception as e:
            print(e)
            return


# 音频合成（edge-tts / vits）并播放
def audio_synthesis(type="edge-tts", text="hi"):
    # 单独开线程播放
    threading.Thread(target=my_play_voice, args=(type, text,)).start()


# 判断字符串是否全为标点符号
def is_punctuation_string(string):
    # 使用正则表达式匹配标点符号
    pattern = r'^[^\w\s]+$'
    return re.match(pattern, string) is not None


def onMessage(ws: websocket.WebSocketApp, message: bytes):
    wssPackage = PushFrame()
    wssPackage.ParseFromString(message)
    logId = wssPackage.logId
    decompressed = gzip.decompress(wssPackage.payload)
    payloadPackage = Response()
    payloadPackage.ParseFromString(decompressed)
    # 发送ack包
    if payloadPackage.needAck:
        sendAck(ws, logId, payloadPackage.internalExt)
    for msg in payloadPackage.messagesList:
        if msg.method == 'WebcastMatchAgainstScoreMessage':
            unPackMatchAgainstScoreMessage(msg.payload)
            continue

        if msg.method == 'WebcastLikeMessage':
            unPackWebcastLikeMessage(msg.payload)
            continue

        if msg.method == 'WebcastMemberMessage':
            unPackWebcastMemberMessage(msg.payload)
            continue
        if msg.method == 'WebcastGiftMessage':
            unPackWebcastGiftMessage(msg.payload)
            continue
        if msg.method == 'WebcastChatMessage':
            data = unPackWebcastChatMessage(msg.payload)

            # print(data)

            content = data['content']
            user_name = data['user']['nickName']

            # 判断弹幕是否以句号或问号结尾，如果是则进行回复
            if content.endswith("。") or content.endswith("？") or content.endswith("?"):
                # 输出当前用户发送的弹幕消息
                print(f"[{user_name}]: {content}")

                # 全为标点符号
                if is_punctuation_string(content):
                    return

                # 换行转为,
                content = content.replace('\n', ',')

                # 含有违禁词/链接
                if profanity.contains_profanity(content) or check_sensitive_words(badwords_path, content) or \
                    is_url_check(content):
                    print(f"违禁词/链接：{content}")
                    return

                # 语言检测
                if lang_check(content, need_lang) is None:
                    return

                if chat_type == "gpt":
                    content = before_promet + content + after_promet
                    # 调用gpt接口，获取返回内容
                    resp_content = get_gpt_resp(user_name, content)
                    if resp_content is not None:
                        # 输出 ChatGPT 返回的回复消息
                        print(f"[AI回复{user_name}]：{resp_content}")
                    else:
                        resp_content = ""
                        print("警告：gpt无返回")
                elif chat_type == "claude":
                    content = before_promet + content + after_promet
                    resp_content = get_claude_resp(content)
                    if resp_content is not None:
                        # 输出 返回的回复消息
                        print(f"[AI回复{user_name}]：{resp_content}")
                    else:
                        resp_content = ""
                        print("警告：claude无返回")
                elif chat_type == "chatterbot":
                    # 生成回复
                    resp_content = bot.get_response(content).text
                elif chat_type == "langchain_pdf":
                    # 只用langchain，不做gpt的调用，可以节省token，做个简单的本地数据搜索
                    resp_contents = docsearch.similarity_search(content)
                    if len(resp_contents) != 0:
                        resp_content = resp_contents[0].page_content
                    else:
                        resp_content = "没有获取到匹配结果。"

                    print(f"[AI回复{user_name}]：{resp_content}")
                elif chat_type == "langchain_pdf+gpt":
                    resp_content = query_func(content)
                    print(f"[AI回复{user_name}]：{resp_content}")
                # elif chat_type == "game":
                #     g1 = game1()
                #     g1.parse_keys_and_simulate_key_press(content.split(), 2)

                    return
                else:
                    # 复读机
                    resp_content = content

                # print("resp_content=" + resp_content)

                # 将 AI 回复记录到日志文件中
                with open(log_file_path, "r+", encoding="utf-8") as f:
                    content = f.read()
                    # 将指针移到文件头部位置（此目的是为了让直播中读取日志文件时，可以一直让最新内容显示在顶部）
                    f.seek(0, 0)
                    # 不过这个实现方式，感觉有点低效
                    f.write(f"[AI回复{user_name}]：{resp_content}\n" + content)

                # 音频合成（edge-tts / vits）并播放
                audio_synthesis(audio_synthesis_type, resp_content)

            continue

        if msg.method == 'WebcastSocialMessage':
            unPackWebcastSocialMessage(msg.payload)
            continue

        if msg.method == 'WebcastRoomUserSeqMessage':
            unPackWebcastRoomUserSeqMessage(msg.payload)
            continue

        if msg.method == 'WebcastUpdateFanTicketMessage':
            unPackWebcastUpdateFanTicketMessage(msg.payload)
            continue

        if msg.method == 'WebcastCommonTextMessage':
            unPackWebcastCommonTextMessage(msg.payload)
            continue

        logging.info('[onMessage] [⌛️方法' + msg.method + '等待解析～] [房间Id：' + liveRoomId + ']')


def unPackWebcastCommonTextMessage(data):
    commonTextMessage = CommonTextMessage()
    commonTextMessage.ParseFromString(data)
    data = json_format.MessageToDict(commonTextMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackWebcastCommonTextMessage] [] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


def unPackWebcastUpdateFanTicketMessage(data):
    updateFanTicketMessage = UpdateFanTicketMessage()
    updateFanTicketMessage.ParseFromString(data)
    data = json_format.MessageToDict(updateFanTicketMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackWebcastUpdateFanTicketMessage] [] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


def unPackWebcastRoomUserSeqMessage(data):
    roomUserSeqMessage = RoomUserSeqMessage()
    roomUserSeqMessage.ParseFromString(data)
    data = json_format.MessageToDict(roomUserSeqMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    logging.info('[unPackWebcastRoomUserSeqMessage] [] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


def unPackWebcastSocialMessage(data):
    socialMessage = SocialMessage()
    socialMessage.ParseFromString(data)
    data = json_format.MessageToDict(socialMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackWebcastSocialMessage] [➕直播间关注消息] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


# 普通消息
def unPackWebcastChatMessage(data):
    chatMessage = ChatMessage()
    chatMessage.ParseFromString(data)
    data = json_format.MessageToDict(chatMessage, preserving_proto_field_name=True)
    logging.info('[unPackWebcastChatMessage] [📧直播间弹幕消息] [房间Id：' + liveRoomId + '] ｜ ' + data['content'])
    # logging.info('[unPackWebcastChatMessage] [📧直播间弹幕消息] [房间Id：' + liveRoomId + '] ｜ ' + json.dumps(data))
    return data


# 礼物消息
def unPackWebcastGiftMessage(data):
    giftMessage = GiftMessage()
    giftMessage.ParseFromString(data)
    data = json_format.MessageToDict(giftMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackWebcastGiftMessage] [🎁直播间礼物消息] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


# xx成员进入直播间消息
def unPackWebcastMemberMessage(data):
    memberMessage = MemberMessage()
    memberMessage.ParseFromString(data)
    data = json_format.MessageToDict(memberMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackWebcastMemberMessage] [🚹🚺直播间成员加入消息] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


# 点赞
def unPackWebcastLikeMessage(data):
    likeMessage = LikeMessage()
    likeMessage.ParseFromString(data)
    data = json_format.MessageToDict(likeMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackWebcastLikeMessage] [👍直播间点赞消息] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


# 解析WebcastMatchAgainstScoreMessage消息包体
def unPackMatchAgainstScoreMessage(data):
    matchAgainstScoreMessage = MatchAgainstScoreMessage()
    matchAgainstScoreMessage.ParseFromString(data)
    data = json_format.MessageToDict(matchAgainstScoreMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # logging.info('[unPackMatchAgainstScoreMessage] [🤷不知道是啥的消息] [房间Id：' + liveRoomId + '] ｜ ' + log)
    return data


# 发送Ack请求
def sendAck(ws, logId, internalExt):
    obj = PushFrame()
    obj.payloadType = 'ack'
    obj.logId = logId
    obj.payloadType = internalExt
    data = obj.SerializeToString()
    ws.send(data, websocket.ABNF.OPCODE_BINARY)
    # logging.info('[sendAck] [🌟发送Ack] [房间Id：' + liveRoomId + '] ====> 房间🏖标题【' + liveRoomTitle + '】')


def onError(ws, error):
    logging.error('[onError] [webSocket Error事件] [房间Id：' + liveRoomId + ']')


def onClose(ws, a, b):
    logging.info('[onClose] [webSocket Close事件] [房间Id：' + liveRoomId + ']')


def onOpen(ws):
    _thread.start_new_thread(ping, (ws,))
    logging.info('[onOpen] [webSocket Open事件] [房间Id：' + liveRoomId + ']')


# 发送ping心跳包
def ping(ws):
    while True:
        obj = PushFrame()
        obj.payloadType = 'hb'
        data = obj.SerializeToString()
        ws.send(data, websocket.ABNF.OPCODE_BINARY)
        logging.info('[ping] [💗发送ping心跳] [房间Id：' + liveRoomId + '] ====> 房间🏖标题【' + liveRoomTitle + '】')
        time.sleep(10)


def wssServerStart(roomId):
    global liveRoomId
    liveRoomId = roomId
    websocket.enableTrace(False)
    webSocketUrl = 'wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&internal_ext=internal_src:dim|wss_push_room_id:'+liveRoomId+'|wss_push_did:7188358506633528844|dim_log_id:20230521093022204E5B327EF20D5CDFC6|fetch_time:1684632622323|seq:1|wss_info:0-1684632622323-0-0|wrds_kvs:WebcastRoomRankMessage-1684632106402346965_WebcastRoomStatsMessage-1684632616357153318&cursor=t-1684632622323_r-1_d-1_u-1_h-1&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&debug=false&maxCacheMessageNumber=20&endpoint=live_pc&support_wrds=1&im_path=/webcast/im/fetch/&user_unique_id=7188358506633528844&device_platform=web&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh&browser_platform=MacIntel&browser_name=Mozilla&browser_version=5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36&browser_online=true&tz_name=Asia/Shanghai&identity=audience&room_id='+liveRoomId+'&heartbeatDuration=0&signature=00000000'
    h = {
        'cookie': 'ttwid='+ttwid,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    # 创建一个长连接
    ws = websocket.WebSocketApp(
        webSocketUrl, on_message=onMessage, on_error=onError, on_close=onClose,
        on_open=onOpen,
        header=h
    )
    ws.run_forever()


def parseLiveRoomUrl(url):
    h = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'cookie': '__ac_nonce=0638733a400869171be51',
    }
    res = requests.get(url=url, headers=h, proxies=proxy)
    global ttwid, roomStore, liveRoomId, liveRoomTitle
    data = res.cookies.get_dict()
    ttwid = data['ttwid']
    res = res.text
    res = re.search(r'<script id="RENDER_DATA" type="application/json">(.*?)</script>', res)
    res = res.group(1)
    res = urllib.parse.unquote(res, encoding='utf-8', errors='replace')
    res = json.loads(res)
    roomStore = res['app']['initialState']['roomStore']
    liveRoomId = roomStore['roomInfo']['roomId']
    liveRoomTitle = roomStore['roomInfo']['room']['title']
    wssServerStart(liveRoomId)


def test():
    url = "https://www.douyin.com/aweme/v1/web/commit/follow/user/?device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh&browser_platform=MacIntel&browser_name=Chrome&browser_version=109.0.0.0&browser_online=true&engine_name=Blink&engine_version=109.0.0.0&os_name=Mac+OS&os_version=10.15.7&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7188358506633528844&msToken=6j75IbD0uth58uE0p2svIf3-bGlzkqLnJ34RfGkr8Ooxgos99KHfw-4HzlJ26GI6C3uTwDUUIthFI0wUocJy2ZAMkpyPrUgGFgcshHRO3vw_kBc9yiZ-4EbErjwp8FI=&X-Bogus=DFSzswVYdOs9-MIISZ-yup7TlqtU"
    h = {
        "accept": "application/json, text/plain, */*",
        # "accept-encoding": "gzip, deflate, br",
        # "accept-language": "zh,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6",
        # "content-length": "26",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": "__ac_nonce=063c22e0b00ef2187712a; __ac_signature=_02B4Z6wo00f01UZsilwAAIDC0rrRUTr27elGTI7AADJcqjRe1hQOZ"
                  ".K4Q4FmO9daZqxwlf.5k4RomG9GZZgMXO3CvtvKJiy9txGxo4HWdJhcwlVYhBiKSGhWCrULSjQEPlsLZ8LgciLILIZO8f; "
                  "ttwid=1%7Cw5daZw41FpoZMR-XIJc-J_4yVhjVtBUBWUPO-v6khXo%7C1673670155"
                  "%7Cd796439337e51fc553cfb64d79ef412b84b3eef18e9e19ebaa1287a829b90db8; douyin.com; "
                  "passport_csrf_token=955106f18f323068c601a6918c27747d; "
                  "passport_csrf_token_default=955106f18f323068c601a6918c27747d; "
                  "s_v_web_id=verify_lcvfzyv4_BZabwp7p_r58g_4G5z_8KHs_lDuazCJCZ9uB; "
                  "passport_assist_user"
                  "=Cj2FisA1wsU1M6ZAOUfBxA5tt48uEnnpcfN8dtT3oivxC3hjFxm0iQwLvZkXjoCnZas0ias8qelCHfDmIZJ5GkgKPEal_vGBVAKPt3vk_68vkfwzRBgsf8APM87d_iaEiBj6_B9X0Gj7vjvTHA_1A0fF9m3QYysg3NS7vbf-ihDlxaYNGImv1lQiAQNaHWg4; n_mh=bUxOCHzZv5szT8QIHfxmgnjoVlZQ1kn7aM-ZW6ndDKY; sso_uid_tt=e1e48ca5f945784a59c3174e16176a61; sso_uid_tt_ss=e1e48ca5f945784a59c3174e16176a61; toutiao_sso_user=fba93355178fb80aafc02d05bfcd0a5c; toutiao_sso_user_ss=fba93355178fb80aafc02d05bfcd0a5c; sid_ucp_sso_v1=1.0.0-KDM0OWJmNzI2ZDQ1NjFmODJkMTY4Y2Q2MDAzMTIzY2FkMTc1YWUwYmQKHQik8Iy7gQMQ7tyIngYY7zEgDDCYxPfbBTgGQPQHGgJsZiIgZmJhOTMzNTUxNzhmYjgwYWFmYzAyZDA1YmZjZDBhNWM; ssid_ucp_sso_v1=1.0.0-KDM0OWJmNzI2ZDQ1NjFmODJkMTY4Y2Q2MDAzMTIzY2FkMTc1YWUwYmQKHQik8Iy7gQMQ7tyIngYY7zEgDDCYxPfbBTgGQPQHGgJsZiIgZmJhOTMzNTUxNzhmYjgwYWFmYzAyZDA1YmZjZDBhNWM; odin_tt=8547fef56c59daf11b0c15312d499833a2be72189dd6aad256dc07c950b8880c52ad37e717a99de93cc971ad3d80d88ffc1b4e6a10be0fd4f05d46ba29e91ac5; passport_auth_status=6929cca1c9119873a9d7fa528ccd5f37%2C; passport_auth_status_ss=6929cca1c9119873a9d7fa528ccd5f37%2C; uid_tt=8c0899f7528059e847f7eddad4210e5c; uid_tt_ss=8c0899f7528059e847f7eddad4210e5c; sid_tt=6c5a7be3caf51c935494a12b4f1c5c13; sessionid=6c5a7be3caf51c935494a12b4f1c5c13; sessionid_ss=6c5a7be3caf51c935494a12b4f1c5c13; LOGIN_STATUS=1; store-region=cn-hn; store-region-src=uid; sid_guard=6c5a7be3caf51c935494a12b4f1c5c13%7C1673670258%7C5183996%7CWed%2C+15-Mar-2023+04%3A24%3A14+GMT; sid_ucp_v1=1.0.0-KGZmOThhNTZlMThiOTEzMTI2MWI0MDIxZGM5MDUyNjVmZmVkMzVhMTgKFwik8Iy7gQMQ8tyIngYY7zEgDDgGQPQHGgJsZiIgNmM1YTdiZTNjYWY1MWM5MzU0OTRhMTJiNGYxYzVjMTM; ssid_ucp_v1=1.0.0-KGZmOThhNTZlMThiOTEzMTI2MWI0MDIxZGM5MDUyNjVmZmVkMzVhMTgKFwik8Iy7gQMQ8tyIngYY7zEgDDgGQPQHGgJsZiIgNmM1YTdiZTNjYWY1MWM5MzU0OTRhMTJiNGYxYzVjMTM; csrf_session_id=f8b3bae210355efd72d7b596b8d59786; tt_scid=yrq-tjQaXEaPz4kTP9WpqNwOnqVy13KMI.snGi6wnZp8P1hduQmhbtqsTOyIhz.O0bd1; download_guide=%223%2F20230114%22; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1674275671220%2C%22type%22%3A1%7D; strategyABtestKey=%221673670871.396%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAlc42G0Nktrm_CVQMfASabMRnI_6GlL2br1i7a8yqTEI%2F1673712000000%2F0%2F1673670871480%2F0%22; home_can_add_dy_2_desktop=%221%22; passport_fe_beating_status=true; msToken=veZvf1xerEu8qj_1IHeP6Tce5JyHlTLZf_YVSJCj5moDg72Q0821Vcqo4ylUrBP75wlGO2xO22kVG9fEsZvWcx6L6nUPhL6LFf6TtpXznJMEA7riXCgfInQgv70a3Go=; msToken=6j75IbD0uth58uE0p2svIf3-bGlzkqLnJ34RfGkr8Ooxgos99KHfw-4HzlJ26GI6C3uTwDUUIthFI0wUocJy2ZAMkpyPrUgGFgcshHRO3vw_kBc9yiZ-4EbErjwp8FI=",
        "origin": "https://www.douyin.com",
        "referer": "https://www.douyin.com/",
        # "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
        # "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "x-secsdk-csrf-token": "000100000001a4af956d5ea10b016b19ba5c287191937c2093fc6b603acc6ee5bed3a6354333173a12ca9498806f"
    }
    data = "type=1&user_id=93865343726"
    res = requests.post(url=url, data=data, headers=h, proxies=proxy).json()
    print(res)


# 十六进制字符串转protobuf格式 （用于快手网页websocket调试分析包体结构）
def hexStrToProtobuf(hexStr):
    # 示例数据
    # hexStr = '08d40210011aeb250a8e010a81010a0b66666731343535323939391206e68595e799bd1a6a68747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31322f32312f424d6a41794d6a45784d5449794d5441304d6a68664d6a67784d4445354e7a67344d5638795832686b4d6a6335587a49324d513d3d5f732e6a7067180120012a04323132300aa8010a9e010a0b79697869616f77753636361209e79fa5e5b08fe6ada61a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31302f30322f31392f424d6a41794d6a45774d4449784f544d304e4442664e6a497a4d4455324d445977587a4a66614751304e444a664d546b335f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a033430330ab6010aac010a0c4c31333130373432373635301212e9bb8ee699a8f09f8c8af09f8c8af09f8c8a1a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31392f31332f424d6a41794d6a45784d546b784d7a4d784d5452664d5441344e5467794d5449334d5638795832686b4e444935587a45304d513d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a033335390ac2010ab8010a104757515053414148445244444145775a121ee69492e4b880e58fa3e8a28be6989fe6989fe98081e7bb99e58c97e699a81a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31322f32312f424d6a41794d6a45784d5449794d5445774d6a4e664d5445314d7a59354d4451324e6c38795832686b4e7a46664f5449355f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a033130330a91010a88010a0f337870323538746a6d6376337a62751209e58699e7949ce8af971a6a68747470733a2f2f70332e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f32302f31372f424d6a41794d6a45784d6a41784e7a4d784e5442664d7a45784d7a4d784f5445784e6c38795832686b4d545530587a49344d513d3d5f732e6a706718012a0233340aac010aa3010a0979756875616e306b64120ce88a8be594a4e1b587e1b69c1a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f30362f31312f30312f424d6a41794d6a41324d5445774d5451334e5452664d5441774d6a51324f4445344f4638795832686b4e444535587a457a4e773d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a0233330a8a010a81010a0c6868686832303033313032391205e888aac2b71a6a68747470733a2f2f70332e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f30332f32322f424d6a41794d6a45784d444d794d6a41784d546c664d6a4d7a4d7a45794d4455304d3138795832686b4e544133587a4d314d513d3d5f732e6a706718012a0233310aab010aa2010a0f3378686d3568677a6e657963666b6b1209e890a8e5bf853536391a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032302f30372f32342f30382f424d6a41794d4441334d6a51774f4449774d4442664d5467344e5455314d5449784e6c38795832686b4d6a4d79587a673d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a0232330a93010a8a010a0f33787569663363746b6e6d38773271120be790aae790aa37313432321a6a68747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31382f31322f424d6a41794d6a45784d5467784d6a45784e4446664d7a45794f5441354f446b304e3138795832686b4e7a6730587a49344e773d3d5f732e6a706718012a0232320a94010a8b010a0f337862677a6a627034777570763567120cefbc87e7bbade99b86efbc821a6a68747470733a2f2f70352e612e7978696d67732e636f6d2f75686561642f41422f323032322f30382f33302f31352f424d6a41794d6a41344d7a41784e5451334e4452664d5441324d6a51334d6a41324e3138795832686b4f545533587a63314e413d3d5f732e6a706718012a0232320aa5010a9c010a0979796473696f73313212054c696b652e1a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31382f31322f424d6a41794d6a45784d5467784d6a51324e4456664d6a4d354d4459774d5455344e5638785832686b4d546731587a51354d773d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a0232310a90010a85010a0a48657969676530353230120be4bba5e6ad8c20f09f8e801a6a68747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31332f31302f424d6a41794d6a45784d544d784d4455354d6a4e664d544d324e6a41304e7a41774d5638785832686b4d6a6779587a51794f413d3d5f732e6a7067180120012a0231320aa8010a9f010a0f33786b623464793435706a797570711206e684a6e6829f1a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f30342f32322f424d6a41794d6a45784d4451794d6a41774d445a664e4445794f446b324d545931587a4a66614751324e4456664f446b355f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a0231310aa5010a9c010a08776a353431383830120ae88b8fe791bee699a82f1a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f30332f30302f424d6a41794d6a45784d444d774d4449344e546c664d6a41354e6a45794e544d31587a4666614751304d7a6c664e444d785f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a0231310abc010ab3010a0f33786334746a7a376e7875636561791216e7a9bfe5b1b1e794b2efbc88696b756ee59ba2efbc891a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f30382f32362f31312f424d6a41794d6a41344d6a59784d5451334d4442664d6a4d314d7a41314d4449774d3138795832686b4e444d79587a4d7a4e673d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a0231300a8c010a84010a0957535162616f353230120fe5b08f20e5a88120e5b09120e380821a6668747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31332f31392f424d6a41794d6a45784d544d784f5445354d5446664f5455314e4449304f445578587a4a666147517a4e5452664e4449785f732e6a706718012a01330a8f010a87010a0f337834646178626768746a78716979120ce7a78be8be9ee1b587e1b69c1a6668747470733a2f2f70332e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31342f31312f424d6a41794d6a45784d5451784d544d7a4d544a664e7a55354d7a63774d446b31587a4a66614751784f544e664e5459315f732e6a706718012a01330a8d010a85010a0f3378723937706975747768326d7a321206e791bee4b8811a6a68747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032312f30342f32332f32312f424d6a41794d5441304d6a4d794d5445304e544a664d5463794d7a55304f4463304d4638795832686b4f546378587a59354e513d3d5f732e6a706718012a01330ab0010aa8010a0d6c713431383835343138386868120de585b3e4ba8ee58a8920e5bcb71a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f30352f32332f424d6a41794d6a45784d4455794d7a4d334e544a664d54517a4f44497a4e6a67784d6c38795832686b4d544578587a67324f413d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a01330a8b010a83010a0e4c544431353933313731353337371209e4bba5e6a4bfe383bb1a6668747470733a2f2f70332e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f30372f31392f424d6a41794d6a45784d4463784f544d314d545a664d5441314d5463784e4459334e6c38795832686b4f444579587a55315f732e6a706718012a01330a89010a83010a0b64796c3230303830363130120ce5b08fe5b08fe5a79ce99c961a6668747470733a2f2f70342e612e7978696d67732e636f6d2f75686561642f41422f323032322f31302f31362f31312f424d6a41794d6a45774d5459784d5455354e5442664f4449304e7a517a4e545535587a4a66614751334d7a42664e5445335f732e6a70672a01320ab7010ab1010a0f3378727a33667a69737438717334611218e5bf98e5b79de38088e5b7b2e69c89e58584e5bc9fe380891a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31342f31312f424d6a41794d6a45784d5451784d54557a4d6a42664f4441304e444d794f545579587a4666614751304d7a52664d7a4d785f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e7372632a01320a90010a8a010a0e796f6e6773686974756f7a68616e1210e5b08fe58b87e5a3ab2de99988e8b68a1a6668747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f30352f32382f31332f424d6a41794d6a41314d6a67784d7a51354d445a664e7a59304f44517a4d7a6b35587a4a66614751794d6a56664e544d7a5f732e6a70672a01320a8d010a87010a0f3378746d706b6167627536766e7139120ce5ad90e792a9e1b587e1b69c1a6668747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f31302f33312f31312f424d6a41794d6a45774d7a45784d544d784e4468664e6a45324d4445304d444d30587a4a66614751314e446c664d54497a5f732e6a70672a01320a89010a83010a0f4c4a483532304c4a31333134656d6f1204f09f88b71a6a68747470733a2f2f70352e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31342f31382f424d6a41794d6a45784d5451784f4441314d4442664d6a67354d4441774f5455314e6c38795832686b4d6a6730587a63794e513d3d5f732e6a70672a01320aa5010a9d010a0f33786967326675743533373872626b1204456e6d681a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f32332f31312f424d6a41794d6a45784d6a4d784d544d784e446c664d6a59324e7a517a4d4455334f5638785832686b4d7a4132587a6b315f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e73726318012a01320ab1010aab010a0f33786d39353268396a393473787a731212e5ad90e792a9efbc88e5b08fe58fb7efbc891a830168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f30372f30302f424d6a41794d6a45784d4463774d4451794e4452664d6a517a4d5463314d6a49354e5638795832686b4e5464664e7a49785f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e7372632a01320aa9010aa3010a0f3378397370326436703272727866391206e585b1e5928c1a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f30372f32382f31322f424d6a41794d6a41334d6a67784d6a55314d7a42664d6a4d354e6a4d774e4455304d3138795832686b4e6a6b35587a45774e413d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e7372632a01320aa5010a9f010a0b4c5a5032303133313479611206e6b3bde4b8801a870168747470733a2f2f616c69696d672e612e7978696d67732e636f6d2f75686561642f41422f323032322f30372f31332f31362f424d6a41794d6a41334d544d784e6a49304e5456664d546b324e4445794f4463334f5638795832686b4f545179587a597a4d673d3d5f732e6a70674030655f306f5f306c5f3530685f3530775f3835712e7372632a01320a9f010a99010a0f3378326e37793865656573766b6879121ee58c97e699a8e79a84e4bfa1e699baefbc88e5b7b2e7b4abe7a082efbc891a6668747470733a2f2f70312e612e7978696d67732e636f6d2f75686561642f41422f323032322f31312f31332f31312f424d6a41794d6a45784d544d784d5441344d6a68664d5467344d44497a4f5441354e5638785832686b4f446b79587a45795f732e6a70672a013220a699a0ebca30'
    with open('t-proto', 'wb') as w:
        w.write(binascii.unhexlify(hexStr))

    parser = StandardParser()

    print(parser)
    with open('t-proto', 'rb') as fh:
        output = parser.parse_message(fh, 'message')
    print(output)
    return output


if audio_synthesis_type == "vits":
    try:
        with open(vits_config_path, "r", encoding="utf-8") as file:
            vits_data = json.load(file)
        
        # 加载说话人配置
        speakers = vits_data["speakers"]

        print("vits配置加载成功。")
    except Exception as e:
        print('加载配置文件失败，请进行修复')
        exit(0)

if chat_type == "claude":
    client = WebClient(token=slack_user_token)

    dm_channel_id = find_direct_message_channel(bot_user_id)
    if not dm_channel_id:
        print("Could not find DM channel with the bot.")
        exit(0)

    last_message_timestamp = None
elif chat_type == "chatterbot":
    from chatterbot import ChatBot  # 导入聊天机器人库

    bot = ChatBot(
        chatterbot_name,  # 聊天机器人名字
        database_uri='sqlite:///' + chatterbot_name  # 数据库URI，数据库用于存储对话历史
    )

try: 
    parseLiveRoomUrl(f"https://live.douyin.com/{room_id}")
except KeyboardInterrupt:
    print('程序被强行退出')
finally:
    print('关闭连接...')
    exit(0)
