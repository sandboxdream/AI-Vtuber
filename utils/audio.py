import time, logging
import requests
import json, threading
import subprocess
import pygame
import queue
import edge_tts
import asyncio
from copy import deepcopy
import aiohttp
import glob
import os

from elevenlabs import generate, play, set_api_key

from .common import Common
from .logger import Configure_logger
from .config import Config


class Audio:
    # 存储消息（待合成音频的弹幕）
    messages = []

    def __init__(self, config_path):  
        self.common = Common()
        self.config = Config(config_path)

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        # 创建消息队列
        self.message_queue = queue.Queue()
        # 创建音频路径队列
        self.voice_tmp_path_queue = queue.Queue()

        # 旧版同步写法
        # threading.Thread(target=self.message_queue_thread).start()
        # 改异步
        threading.Thread(target=lambda: asyncio.run(self.message_queue_thread())).start()

        # 音频合成单独一个线程排队播放
        self.only_play_audio_thread = threading.Thread(target=self.only_play_audio)
        self.only_play_audio_thread.start()


    # 获取本地音频文件夹内所有的音频文件名
    def get_dir_songs_filename(self):
        try:
            song_path = self.config.get("choose_song", "song_path")

            # 使用 glob 模块匹配指定文件夹下的所有音频文件
            audio_files = glob.glob(os.path.join(song_path, '*.mp3')) + \
                        glob.glob(os.path.join(song_path, '*.wav')) + \
                        glob.glob(os.path.join(song_path, '*.flac')) + \
                        glob.glob(os.path.join(song_path, '*.aac')) + \
                        glob.glob(os.path.join(song_path, '*.ogg')) + \
                        glob.glob(os.path.join(song_path, '*.m4a'))


            # 提取文件名
            file_names = [os.path.basename(file) for file in audio_files]
            # 提取文件名（去除文件后缀）
            # file_names = [os.path.splitext(os.path.basename(file))[0] for file in audio_files]

            logging.info("获取到本地音频文件名列表如下：")
            logging.info(file_names)
        
            return file_names
        except Exception as e:
            logging.error(e)
            return None


    # 音频合成消息队列线程
    async def message_queue_thread(self):
        logging.info("创建音频合成消息队列线程")
        while True:  # 无限循环，直到队列为空时退出
            try:
                message = self.message_queue.get()
                logging.debug(message)
                await self.my_play_voice(message)
                self.message_queue.task_done()

                # 加个延时 降低点edge-tts的压力
                time.sleep(0.5)
            except Exception as e:
                logging.error(e)

    # 请求VITS接口获取合成后的音频路径
    def vits_fast_api(self, vits_api_ip_port="http://127.0.0.1:7860", character="ikaros", language="日语", text="こんにちわ。", speed=1):
        try:
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
            logging.error(e)
            return None
    

    # 调用so-vits-svc的api
    async def so_vits_svc_api(self, audio_path=""):
        try:
            url = f"{self.config.get('so_vits_svc', 'api_ip_port')}/wav2wav"
            
            params = {
                "audio_path": audio_path,
                "tran": self.config.get("so_vits_svc", "tran"),
                "spk": self.config.get("so_vits_svc", "spk"),
                "wav_format": self.config.get("so_vits_svc", "wav_format")
            }

            # logging.info(params)

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=params) as response:
                    if response.status == 200:
                        output_path = "out/" + self.common.get_bj_time(4) + ".wav"  # Replace with the desired path to save the output WAV file
                        with open(output_path, "wb") as f:
                            f.write(await response.read())
                        logging.debug(f"Conversion completed. Output WAV file saved:{output_path}")

                        return output_path
                    else:
                        logging.error(await response.text())

                        return None
        except Exception as e:
            logging.error(e)


    # 音频合成（edge-tts / vits）并播放
    def audio_synthesis(self, message):
        try:
            logging.debug(message)

            # 判断是否是点歌模式
            if message['type'] == "song":
                self.voice_tmp_path_queue.put(message['content'])
                return

            # 中文语句切分
            sentences = self.common.split_sentences(message['content'])
            for s in sentences:
                message_copy = deepcopy(message)  # 创建 message 的副本
                message_copy["content"] = s  # 修改副本的 content
                # logging.info(f"s={s}")
                self.message_queue.put(message_copy)  # 将副本放入队列中
            # 单独开线程播放
            # threading.Thread(target=self.my_play_voice, args=(type, data, config, content,)).start()
        except Exception as e:
            logging.error(e)
            return


    # 播放音频
    async def my_play_voice(self, message):
        try:
            logging.debug(f"合成音频前的原始数据：{message['content']}")
            message["content"] = self.common.remove_extra_words(message["content"], message["config"]["max_len"], message["config"]["max_char_len"])
            # logging.info("裁剪后的合成文本:" + text)

            message["content"] = message["content"].replace('\n', '。')
        except Exception as e:
            logging.error(e)
            return

        if message["type"] == "vits":
            try:
                # 语言检测
                language = self.common.lang_check(message["content"])

                # 自定义语言名称（需要匹配请求解析）
                language_name_dict = {"en": "英语", "zh": "中文", "jp": "日语"}  

                if language in language_name_dict:
                    language = language_name_dict[language]
                else:
                    language = "日语"  # 无法识别出语言代码时的默认值

                # logging.info("language=" + language)

                # 调用接口合成语音
                data_json = self.vits_fast_api(message["data"]["api_ip_port"], message["data"]["character"], language, message["content"], message["data"]["speed"])
                # logging.info(data_json)

                voice_tmp_path = data_json["data"][1]["name"]
                # print(f"voice_tmp_path={voice_tmp_path}")

                if True == self.config.get("so_vits_svc", "enable"):
                    voice_tmp_path = await self.so_vits_svc_api(audio_path=voice_tmp_path)
                    # print(f"voice_tmp_path={voice_tmp_path}")

                self.voice_tmp_path_queue.put(voice_tmp_path)
            except Exception as e:
                logging.error(e)
                return
        elif message["type"] == "edge-tts":
            try:
                voice_tmp_path = './out/' + self.common.get_bj_time(4) + '.mp3'
                # 过滤" '字符
                message["content"] = message["content"].replace('"', '').replace("'", '').replace(" ", ',')
                # 使用 Edge TTS 生成回复消息的语音文件
                communicate = edge_tts.Communicate(text=message["content"], voice=message["data"]["voice"], rate=message["data"]["rate"], volume=message["data"]["volume"])
                await communicate.save(voice_tmp_path)

                # logging.info(f"voice_tmp_path={voice_tmp_path}")

                if True == self.config.get("so_vits_svc", "enable"):
                    voice_tmp_path = await self.so_vits_svc_api(audio_path=os.path.abspath(voice_tmp_path))
                    # print(f"voice_tmp_path={voice_tmp_path}")

                self.voice_tmp_path_queue.put(voice_tmp_path)
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


    # 只进行音频合成   
    def only_play_audio(self):
        try:
            pygame.mixer.init()
            while True:
                voice_tmp_path = self.voice_tmp_path_queue.get()  # 从队列中获取音频文件路径
                if voice_tmp_path is None:  # 队列为空时退出循环
                    continue
                
                pygame.mixer.music.load(voice_tmp_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                pygame.mixer.music.stop()

                time.sleep(1)  # 添加延时，暂停执行1秒钟

            pygame.mixer.quit()
        except Exception as e:
            logging.error(e)


    # 停止当前播放的音频
    def stop_current_audio(self):
        pygame.mixer.music.fadeout(1000)
