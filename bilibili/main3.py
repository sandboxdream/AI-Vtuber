# 导入所需的库
import json, re, os
import subprocess
import traceback
from copy import deepcopy
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import aiohttp, asyncio
import langid

import pygame
from bilibili_api import live, sync

import time

from profanity import profanity


# 读取配置文件信息
with open("config.json", "r", encoding='utf-8') as jsonfile:
    config_data = json.load(jsonfile)

try:
    # 设置会话初始值
    session_config = {'msg': [{"role": "system", "content": config_data['chatgpt']['preset']}]}
    sessions = {}
    current_key_index = 0

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

    # Bilibili 直播间 ID
    room_id = config_data["room_display_id"]

    # 初始化 Bilibili 直播间和 TTS 语音
    room = live.LiveDanmaku(room_id)

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


# 判断字符串是否全为标点符号
def is_punctuation_string(string):
    # 使用正则表达式匹配标点符号
    pattern = r'^[^\w\s]+$'
    return re.match(pattern, string) is not None


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
elif chat_type == "game":
    from game1 import game1


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


# 请求VITS接口获取合成后的音频路径
async def get_data(character="ikaros", language="日语", text="こんにちわ。", speed=1):
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url=API_URL, json=data_json) as response:
                result = await response.read()
                # print(result)
                ret = json.loads(result)
        return ret
    except Exception as e:
        print(e)
        return None


# 音频合成（edge-tts / vits / elevenlabs）并播放
async def audio_synthesis(type="edge-tts", text="hi"):
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
            data_json = await get_data(character, language, text, speed)
            # print(data_json)
        except Exception as e:
            print(e)
            return

        voice_tmp_path = data_json["data"][1]["name"]

        try:
            # 播放生成的语音文件
            pygame.mixer.init()
            pygame.mixer.music.load(voice_tmp_path)

            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(e)
            return
    elif type == "edge-tts":
        voice_tmp_path = './out/' + get_bj_time(2) + '.mp3'
        # 过滤" '字符
        text = text.replace('"', '').replace("'", '').replace(" ", ',')
        # 使用 Edge TTS 生成回复消息的语音文件
        cmd = f'edge-tts --voice {tts_voice} --text "{text}" --write-media {voice_tmp_path}'
        subprocess.run(cmd, shell=True)

        await asyncio.sleep(0.5)

        try:
            # 播放生成的语音文件
            pygame.mixer.init()
            pygame.mixer.music.load(voice_tmp_path)

            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(e)
            return
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


@room.on('DANMU_MSG')
async def on_danmaku(event):
    """
    处理直播间弹幕事件
    :param event: 弹幕事件数据
    """
    content = event["data"]["info"][1]  # 获取弹幕内容
    user_name = event["data"]["info"][2][1]  # 获取发送弹幕的用户昵称

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

        # 根据聊天类型执行不同逻辑
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
            print(f"[AI回复{user_name}]：{resp_content}")
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
        elif chat_type == "game":
            g1 = game1()
            g1.parse_keys_and_simulate_key_press(content.split(), 2)

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
        await audio_synthesis(audio_synthesis_type, resp_content)


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

try: 
    # 启动 Bilibili 直播间连接
    sync(room.connect())
except KeyboardInterrupt:
    print('程序被强行退出')
finally:
    print('关闭连接...')
    exit(0)
