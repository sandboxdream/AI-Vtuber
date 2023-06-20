import time, logging
import requests
import json, threading
import subprocess
import pygame
import queue

from elevenlabs import generate, play, set_api_key

from .common import Common
from .logger import Configure_logger


class Audio:
    common = None
    message_queue = None
    # 存储消息（待合成音频的弹幕）
    messages = []

    def __init__(self):  
        self.common = Common()

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        # 创建队列
        self.message_queue = queue.Queue()

        threading.Thread(target=self.message_queue_thread).start()


    def message_queue_thread(self):
        logging.info("创建音频合成消息队列线程")
        while True:  # 无限循环，直到队列为空时退出
            message = self.message_queue.get()
            logging.debug(message)
            self.my_play_voice(message)
            self.message_queue.task_done()


    # 请求VITS接口获取合成后的音频路径
    def get_data(self, vits_api_ip_port="http://127.0.0.1:7860", character="ikaros", language="日语", text="こんにちわ。", speed=1):
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
            #         # logging.info(result)
            #         ret = json.loads(result)
            # return ret
        except Exception as e:
            logging.info(e)
            return None
    

    # 音频合成（edge-tts / vits）并播放
    def audio_synthesis(self, type, data, config, content):
        message = {
            "type": type,
            "data": data,
            "config": config,
            "content": content
        }
        logging.debug(message)
        self.message_queue.put(message)
        # 单独开线程播放
        # threading.Thread(target=self.my_play_voice, args=(type, data, config, content,)).start()


    # 播放音频
    def my_play_voice(self, message):
        logging.debug(f"合成音频前的原始数据：{message['content']}")
        message["content"] = self.common.remove_extra_words(message["content"], message["config"]["max_len"], message["config"]["max_char_len"])
        # logging.info("裁剪后的合成文本:" + text)

        message["content"] = message["content"].replace('\n', '。')

        if message["type"] == "vits":
            # 语言检测
            language = self.common.lang_check(message["content"])

            # 自定义语言名称（需要匹配请求解析）
            language_name_dict = {"en": "英语", "zh": "中文", "jp": "日语"}  

            if language in language_name_dict:
                language = language_name_dict[language]
            else:
                language = "日语"  # 无法识别出语言代码时的默认值

            # logging.info("language=" + language)

            try:
                # 调用接口合成语音
                data_json = self.get_data(message["data"]["api_ip_port"], message["data"]["character"], language, message["content"], message["data"]["speed"])
                # logging.info(data_json)
            except Exception as e:
                logging.error(e)
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
                logging.error(e)
        elif message["type"] == "edge-tts":
            voice_tmp_path = './out/' + self.common.get_bj_time(4) + '.mp3'
            # 过滤" '字符
            message["content"] = message["content"].replace('"', '').replace("'", '').replace(" ", ',')
            # 使用 Edge TTS 生成回复消息的语音文件
            # 注意此处，在打包整合包时，需要改为 venv\python.exe venv\Scripts\edge-tts.exe
            cmd = f'edge-tts --voice {message["data"]["voice"]} --text "{message["content"]}" --write-media {voice_tmp_path} --rate={message["data"]["rate"]} --volume={message["data"]["volume"]}'
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
                logging.error(e)
        elif message["type"] == "elevenlabs":
            try:
                # 如果配置了密钥就设置上0.0
                if message["data"]["elevenlabs_api_key"] != "":
                    set_api_key(message["data"]["elevenlabs_api_key"])

                audio = generate(
                    text=message["content"],
                    voice=message["data"]["elevenlabs_voice"],
                    model=message["data"]["elevenlabs_model"]
                )

                play(audio)
            except Exception as e:
                logging.error(e)
                return