import threading
import json
import time
import requests

# 导入所需的库
import json, threading
import subprocess

import pygame

from elevenlabs import generate, play, set_api_key

from .common import Common

common = Common()

class Audio:
    # def get_vits_speakers(vits_config_path):
    #     try:
    #         with open(vits_config_path, "r", encoding="utf-8") as file:
    #             vits_data = json.load(file)
            
    #         # 加载说话人配置
    #         speakers = vits_data["speakers"]

    #         return speakers
    #     except Exception as e:
    #         print('加载配置文件失败，请进行修复')
    #         return None

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
            #         # print(result)
            #         ret = json.loads(result)
            # return ret
        except Exception as e:
            print(e)
            return None
    

    # 音频合成（edge-tts / vits）并播放
    def audio_synthesis(self, type, data, config, content):
        # 单独开线程播放
        threading.Thread(target=self.my_play_voice, args=(type, data, config, content,)).start()


    # 播放音频
    def my_play_voice(self, type, data, config, content):
        content = common.remove_extra_words(content, config["max_len"], config["max_char_len"])
        # print("裁剪后的合成文本:" + text)

        content = content.replace('\n', '。')

        if type == "vits":
            # 语言检测
            language = common.lang_check(content)

            # 自定义语言名称（需要匹配请求解析）
            language_name_dict = {"en": "英语", "zh": "中文", "jp": "日语"}  

            if language in language_name_dict:
                language = language_name_dict[language]
            else:
                language = "日语"  # 无法识别出语言代码时的默认值

            # print("language=" + language)

            try:
                # 调用接口合成语音
                data_json = self.get_data(data["api_ip_port"], data["character"], language, content, data["speed"])
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
            voice_tmp_path = './out/' + common.get_bj_time(2) + '.mp3'
            # 过滤" '字符
            content = content.replace('"', '').replace("'", '').replace(" ", ',')
            # 使用 Edge TTS 生成回复消息的语音文件
            cmd = f'edge-tts --voice {data["voice"]} --text "{content}" --write-media {voice_tmp_path}'
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
                if data["elevenlabs_api_key"] != "":
                    set_api_key(data["elevenlabs_api_key"])

                audio = generate(
                    text=content,
                    voice=data["elevenlabs_voice"],
                    model=data["elevenlabs_model"]
                )

                play(audio)
            except Exception as e:
                print(e)
                return