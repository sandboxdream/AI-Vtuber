import keyboard
import pyaudio
import wave
import numpy as np
import speech_recognition as sr
import logging, time
import threading
import sys, os
import signal

from aip import AipSpeech

from utils.common import Common
from utils.logger import Configure_logger
from utils.config import Config
from utils.my_handle import My_handle


def start_server():
    global thread, do_listen_and_commit_thread, stop_do_listen_and_commit_thread_event

    thread = None
    do_listen_and_commit_thread = None
    stop_do_listen_and_commit_thread_event = threading.Event()

    common = Common()
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)

    config_path = "config.json"
    config = Config(config_path)

    my_handle = My_handle(config_path)
    if my_handle is None:
        logging.error("程序初始化失败！")
        exit(0)

    cooldown = 0.3 # 冷却时间 0.3 秒
    last_pressed = 0


    # 录音功能(录音时间过短进入openai的语音转文字会报错，请一定注意)
    def record_audio():
        pressdown_num = 0
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        WAVE_OUTPUT_FILENAME = "out/record.wav"
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        frames = []
        print("Recording...")
        flag = 0
        while 1:
            while keyboard.is_pressed('RIGHT_SHIFT'):
                flag = 1
                data = stream.read(CHUNK)
                frames.append(data)
                pressdown_num = pressdown_num + 1
            if flag:
                break
        print("Stopped recording.")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        if pressdown_num >= 5:         # 粗糙的处理手段
            return 1
        else:
            print("杂鱼杂鱼，好短好短(录音时间过短,按右shift重新录制)")
            return 0


    # THRESHOLD 设置音量阈值,默认值800.0,根据实际情况调整  silence_threshold 设置沉默阈值，根据实际情况调整
    def audio_listen(volume_threshold=800.0, silence_threshold=15):
        audio = pyaudio.PyAudio()

        # 设置音频参数
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 1024

        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        frames = []  # 存储录制的音频帧

        is_speaking = False  # 是否在说话
        silent_count = 0  # 沉默计数
        speaking_flag = False   #录入标志位 不重要

        while True:
            # 读取音频数据
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.short)
            max_dB = np.max(audio_data)
            # print(max_dB)
            if max_dB > volume_threshold:
                is_speaking = True
                silent_count = 0
            elif is_speaking is True:
                silent_count += 1

            if is_speaking is True:
                frames.append(data)
                if speaking_flag is False:
                    logging.info("[录入中……]")
                    speaking_flag = True

            if silent_count >= silence_threshold:
                break

        logging.info("[语音录入完成]")

        # 将音频保存为WAV文件
        '''with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))'''
        return frames
    

    # 执行录音、识别&提交
    def do_listen_and_commit(status=True):
        global stop_do_listen_and_commit_thread_event

        while True:
            # 检查是否收到停止事件
            if stop_do_listen_and_commit_thread_event.is_set():
                logging.info(f'停止录音~')
                break
        
            # 根据接入的语音识别类型执行
            if "baidu" == talk_config["type"]:
                # 设置音频参数
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 16000
                WAVE_OUTPUT_FILENAME = './out/baidu_' + common.get_bj_time(4) + '.wav'

                frames = audio_listen(talk_config["volume_threshold"], talk_config["silence_threshold"])

                # 将音频保存为WAV文件
                with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))

                # 读取音频文件
                with open(WAVE_OUTPUT_FILENAME, 'rb') as fp:
                    audio = fp.read()

                # 初始化 AipSpeech 对象
                baidu_client = AipSpeech(talk_config["baidu"]["app_id"], talk_config["baidu"]["api_key"], talk_config["baidu"]["secret_key"])

                # 识别音频文件
                res = baidu_client.asr(audio, 'wav', 16000, {
                    'dev_pid': 1536,
                })
                if res['err_no'] == 0:
                    content = res['result'][0]

                    # 输出识别结果
                    logging.info("识别结果：" + content)
                    user_name = config.get("talk", "username")

                    my_handle.commit_handle(user_name, content)
                else:
                    logging.error(f"百度接口报错：{res}")  
            elif "google" == talk_config["type"]:
                # 创建Recognizer对象
                r = sr.Recognizer()

                try:
                    # 打开麦克风进行录音
                    with sr.Microphone() as source:
                        logging.info(f'录音中...')
                        # 从麦克风获取音频数据
                        audio = r.listen(source)
                        logging.info("成功录制")

                        # 进行谷歌实时语音识别 en-US zh-CN ja-JP
                        content = r.recognize_google(audio, language=config.get("talk", "google", "tgt_lang"))

                        # 输出识别结果
                        # logging.info("识别结果：" + content)
                        user_name = config.get("talk", "username")

                        my_handle.commit_handle(user_name, content)
                except sr.UnknownValueError:
                    logging.warning("无法识别输入的语音")
                except sr.RequestError as e:
                    logging.error("请求出错：" + str(e))
            
            if not status:
                return


    def on_key_press(event):
        global do_listen_and_commit_thread, stop_do_listen_and_commit_thread_event

        if event.name in ['z', 'Z', 'c', 'C'] and keyboard.is_pressed('ctrl'):
            print("退出程序")

            os._exit(0)
        
        # 按键CD
        current_time = time.time()
        if current_time - last_pressed < cooldown:
            return
        

        """
        触发按键部分的判断
        """
        trigger_key_lower = None
        stop_trigger_key_lower = None

        # trigger_key是字母, 整个小写
        if trigger_key.isalpha():
            trigger_key_lower = trigger_key.lower()

        # stop_trigger_key是字母, 整个小写
        if stop_trigger_key.isalpha():
            stop_trigger_key_lower = stop_trigger_key.lower()
        
        if trigger_key_lower:
            if event.name == trigger_key or event.name == trigger_key_lower:
                logging.info(f'检测到单击键盘 {event.name}，即将开始录音~')
            elif event.name == stop_trigger_key or event.name == stop_trigger_key_lower:
                logging.info(f'检测到单击键盘 {event.name}，即将停止录音~')
                stop_do_listen_and_commit_thread_event.set()
                return
            else:
                return
        else:
            if event.name == trigger_key:
                logging.info(f'检测到单击键盘 {event.name}，即将开始录音~')
            elif event.name == stop_trigger_key:
                logging.info(f'检测到单击键盘 {event.name}，即将停止录音~')
                stop_do_listen_and_commit_thread_event.set()
                return
            else:
                return

        # 是否启用连续对话模式
        if talk_config["continuous_talk"]:
            stop_do_listen_and_commit_thread_event.clear()
            do_listen_and_commit_thread = threading.Thread(target=do_listen_and_commit, args=(True,))
            do_listen_and_commit_thread.start()
        else:
            stop_do_listen_and_commit_thread_event.clear()
            do_listen_and_commit_thread = threading.Thread(target=do_listen_and_commit, args=(False,))
            do_listen_and_commit_thread.start()


    # 按键监听
    def key_listener():
        # 注册按键按下事件的回调函数
        keyboard.on_press(on_key_press)

        try:
            # 进入监听状态，等待按键按下
            keyboard.wait()
        except KeyboardInterrupt:
            os._exit(0)

    talk_config = config.get("talk")
    # 从配置文件中读取触发键的字符串配置
    trigger_key = talk_config["trigger_key"]
    stop_trigger_key = talk_config["stop_trigger_key"]

    logging.info(f'单击键盘 {trigger_key} 按键进行录音喵~')

    # 创建并启动按键监听线程
    thread = threading.Thread(target=key_listener)
    thread.start()


    # 起飞
    # audio_listen_google()


# 退出程序
def exit_handler(signum, frame):
    print("Received signal:", signum)

    threading.current_thread().exit()

    os._exit(0)


if __name__ == '__main__':
    # 键盘监听线程
    thread = None
    do_listen_and_commit_thread = None
    stop_do_listen_and_commit_thread_event = None

    signal.signal(signal.SIGINT, exit_handler)
    signal.signal(signal.SIGTERM, exit_handler)

    start_server()

    thread.join() # 等待子线程退出

    os._exit(0)
