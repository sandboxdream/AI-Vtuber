import os
import logging

from .config import Config
from .common import Common
from .audio import Audio
from .logger import Configure_logger


class My_handle():
    # common工具类
    common = None
    # 配置信息
    config = None
    audio = None

    room_id = None
    proxy = None
    # proxy = {
    #     "http": "http://127.0.0.1:10809",
    #     "https": "http://127.0.0.1:10809"
    # }
    session_config = None
    sessions = {}
    current_key_index = 0

    # 直播间号
    room_id = None

    before_prompt = None
    after_prompt = None

    # 过滤配置
    filter_config = None

    chat_type = None

    need_lang = None

    # openai
    openai_config = None
    # chatgpt
    chatgpt_config = None
    # claude
    claude_config = None
    # chatterbot
    chatterbot_config = None
    # langchain_pdf
    langchain_pdf_config = None
    # chatglm
    chatglm_config = None
    # langchain_pdf_local
    langchain_pdf_local_config = None

    # 音频合成使用技术
    audio_synthesis_type = None

    log_file_path = None


    def __init__(self, config_path):        
        self.common = Common()
        self.config = Config(config_path)
        self.audio = Audio()
        
        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.proxy = None

        try:
            
            # 设置会话初始值
            self.session_config = {'msg': [{"role": "system", "content": self.config.get('chatgpt', 'preset')}]}
            self.sessions = {}
            self.current_key_index = 0

            # 直播间号
            self.room_id = self.config.get("room_display_id")

            self.before_prompt = self.config.get("before_prompt")
            self.after_prompt = self.config.get("after_prompt")

            # 过滤配置
            self.filter_config = self.config.get("filter")

            self.chat_type = self.config.get("chat_type")

            self.need_lang = self.config.get("need_lang")

            # openai
            self.openai_config = self.config.get("openai")
            # chatgpt
            self.chatgpt_config = self.config.get("chatgpt")
            # claude
            self.claude_config = self.config.get("claude")
            # chatterbot
            self.chatterbot_config = self.config.get("chatterbot")
            # langchain_pdf
            self.langchain_pdf_config = self.config.get("langchain_pdf")
            # chatglm
            self.chatglm_config = self.config.get("chatglm")
            # langchain_pdf_local
            self.langchain_pdf_local_config = self.config.get("langchain_pdf_local")
            

            # 音频合成使用技术
            self.audio_synthesis_type = self.config.get("audio_synthesis_type")

            logging.info("配置文件加载成功。")
        except Exception as e:
            logging.info(e)
            return None


        # 聊天相关类实例化
        if self.chat_type == "gpt":
            from utils.chatgpt import Chatgpt

            self.chatgpt = Chatgpt(self.openai_config, self.chatgpt_config)
        elif self.chat_type == "claude":
            from utils.claude import Claude

            self.claude = Claude(self.claude_config)
        elif self.chat_type == "chatterbot":
            from chatterbot import ChatBot  # 导入聊天机器人库

            try:
                self.bot = ChatBot(
                    self.chatterbot_config["name"],  # 聊天机器人名字
                    database_uri='sqlite:///' + self.chatterbot_config["db_path"]  # 数据库URI，数据库用于存储对话历史
                )
            except Exception as e:
                logging.info(e)
                exit(0)
        elif self.chat_type == "langchain_pdf" or self.chat_type == "langchain_pdf+gpt":
            from utils.langchain_pdf import Langchain_pdf

            self.langchain_pdf = Langchain_pdf(self.langchain_pdf_config, self.chat_type)
        elif self.chat_type == "chatglm":
            from utils.chatglm import Chatglm

            self.chatglm = Chatglm(self.chatglm_config)
        elif self.chat_type == "langchain_pdf_local":
            from utils.langchain_pdf_local import Langchain_pdf_local

            self.langchain_pdf = Langchain_pdf_local(self.langchain_pdf_local_config, self.chat_type)
        elif self.chat_type == "game":
            exit(0)


        # 日志文件路径
        self.log_file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        if os.path.isfile(self.log_file_path):
            logging.info(f'{self.log_file_path} 日志文件已存在，跳过')
        else:
            with open(self.log_file_path, 'w') as f:
                f.write('')
                logging.info(f'{self.log_file_path} 日志文件已创建')


    def get_room_id(self):
        return self.room_id
    

    def commit_handle(self, user_name, content):
        # 判断弹幕是否以xx起始，如果不是则返回
        if self.filter_config["before_must_str"] and not any(content.startswith(prefix) for prefix in self.filter_config["before_must_str"]):
            return
        else:
            for prefix in self.filter_config["before_must_str"]:
                if content.startswith(prefix):
                    content = content[len(prefix):]  # 删除匹配的开头
                    break

        # 判断弹幕是否以xx结尾，如果不是则返回
        if self.filter_config["after_must_str"] and not any(content.endswith(prefix) for prefix in self.filter_config["after_must_str"]):
            return
        else:
            for prefix in self.filter_config["after_must_str"]:
                if content.endswith(prefix):
                    content = content[:-len(prefix)]  # 删除匹配的结尾
                    break

        # 输出当前用户发送的弹幕消息
        logging.info(f"[{user_name}]: {content}")

        # 全为标点符号
        if self.common.is_punctuation_string(content):
            return

        # 换行转为,
        content = content.replace('\n', ',')

        # 含有违禁词/链接
        if self.common.profanity_content(content) or self.common.check_sensitive_words2(self.filter_config["badwords_path"], content) or \
            self.common.is_url_check(content):
            logging.warning(f"违禁词/链接：{content}")
            return

        # 语言检测
        if self.common.lang_check(content, self.need_lang) is None:
            logging.warning("语言检测不通过，已过滤")
            return

        # 根据聊天类型执行不同逻辑
        if self.chat_type == "gpt":
            content = self.before_prompt + content + self.after_prompt
            # 调用gpt接口，获取返回内容
            resp_content = self.chatgpt.get_gpt_resp(user_name, content)
            if resp_content is not None:
                # 输出 ChatGPT 返回的回复消息
                logging.info(f"[AI回复{user_name}]：{resp_content}")
            else:
                resp_content = ""
                logging.info("警告：gpt无返回")
        elif self.chat_type == "claude":
            content = self.before_prompt + content + self.after_prompt
            resp_content = self.claude.get_claude_resp(content)
            if resp_content is not None:
                # 输出 返回的回复消息
                logging.info(f"[AI回复{user_name}]：{resp_content}")
            else:
                resp_content = ""
                logging.info("警告：claude无返回")
        elif self.chat_type == "chatterbot":
            # 生成回复
            resp_content = self.bot.get_response(content).text
            logging.info(f"[AI回复{user_name}]：{resp_content}")
        elif self.chat_type == "langchain_pdf" or self.chat_type == "langchain_pdf+gpt":
            # 只用langchain，不做gpt的调用，可以节省token，做个简单的本地数据搜索
            resp_content = self.langchain_pdf.get_langchain_pdf_resp(self.chat_type, content)

            logging.info(f"[AI回复{user_name}]：{resp_content}")
        elif self.chat_type == "chatglm":
            # 生成回复
            resp_content = self.chatglm.get_chatglm_resp(content)
            logging.info(f"[AI回复{user_name}]：{resp_content}")
        elif self.chat_type == "langchain_pdf_local":
            resp_content = self.langchain_pdf.get_langchain_pdf_local_resp(self.chat_type, content)

            print(f"[AI回复{user_name}]：{resp_content}")
        elif self.chat_type == "game":
            return
            g1 = game1()
            g1.parse_keys_and_simulate_key_press(content.split(), 2)

            return
        else:
            # 复读机
            resp_content = content

        # logger.info("resp_content=" + resp_content)

        # 将 AI 回复记录到日志文件中
        # with open(self.log_file_path, "r+", encoding="utf-8") as f:
        #     content = f.read()
        #     # 将指针移到文件头部位置（此目的是为了让直播中读取日志文件时，可以一直让最新内容显示在顶部）
        #     f.seek(0, 0)
        #     # 不过这个实现方式，感觉有点低效
        #     f.write(f"[AI回复{user_name}]：{resp_content}\n" + content)


        # 音频合成（edge-tts / vits）并播放
        self.audio.audio_synthesis(self.audio_synthesis_type, self.config.get(self.audio_synthesis_type), self.filter_config, resp_content)

