import keyboard
import pyaudio
import wave
import numpy as np
import speech_recognition as sr
import logging
import threading

from utils.common import Common
from utils.logger import Configure_logger
from utils.config import Config
from utils.my_handle import My_handle


def start_server():
    common = Common()
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)

    config_path = "config.json"
    config = Config(config_path)

    my_handle = My_handle(config_path)
    if my_handle is None:
        logging.info("程序初始化失败！")
        exit(0)


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


    def audio_listen():
        audio = pyaudio.PyAudio()

        # 设置音频参数
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        SILENCE_THRESHOLD = 80     # 设置沉默阈值，根据实际情况调整
        THRESHOLD = 800.0            # 设置音量阈值，根据实际情况调整
        WAVE_OUTPUT_FILENAME = "out/record.wav"

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

        print("[等待语音输入]")
        while True:
            # 读取音频数据
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.short)
            max_dB = np.max(audio_data)
            # print(max_dB)
            if max_dB > THRESHOLD:
                is_speaking = True
                silent_count = 0
            elif is_speaking is True:
                silent_count += 1

            if is_speaking is True:
                frames.append(data)

            if silent_count >= SILENCE_THRESHOLD:
                break
        print("[语音输入完成]")
        # 将音频保存为WAV文件
        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        # print("音频保存完成：", WAVE_OUTPUT_FILENAME)
    

    def on_key_press_goole(event):
        # 创建Recognizer对象
        r = sr.Recognizer()

        try:
            # 打开麦克风进行录音
            with sr.Microphone() as source:
                if event.name == trigger_key:
                    logging.info(f'录音中...')
                    # 从麦克风获取音频数据
                    audio = r.listen(source)
                    logging.info("成功录制")
                    # 进行实时语音识别 en-US zh-CN ja-JP
                    text = r.recognize_google(audio, language=config.get("talk", "google", "tgt_lang"))
                    # 输出识别结果
                    # logging.info("识别结果：" + text)

                    content = text
                    user_name = config.get("talk", "username")

                    my_handle.commit_handle(user_name, content)

                    return
        except sr.UnknownValueError:
            logging.warning("无法识别输入的语音")
        except sr.RequestError as e:
            logging.error("请求出错：" + str(e))


    def key_listener():
        # 注册按键按下事件的回调函数
        keyboard.on_press(on_key_press_goole)

        # 进入监听状态，等待按键按下
        keyboard.wait()


    # 从配置文件中读取触发键的字符串配置
    trigger_key = config.get("talk", "google", "trigger_key")

    logging.info(f'单击键盘 {trigger_key} 按键进行录音喵~')

    # 创建并启动按键监听线程
    thread = threading.Thread(target=key_listener)
    thread.start()


    # 起飞
    # audio_listen_google()


if __name__ == '__main__':
    start_server()
