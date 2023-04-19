import subprocess  # 导入子进程模块
from bilibili_api import live, sync  # 导入bilibili直播API库
import json
import aiohttp
import langid

# 拼音和模拟按键库
import pypinyin
import pykakasi
import pyautogui
import random

# vits配置文件路径(注意路径转义问题)
vits_config_path = "E:\\GitHub_pro\\VITS-fast-fine-tuning\\inference\\finetune_speaker.json"
# api的ip和端口，注意书写格式
vits_api_ip_port = "http://127.0.0.1:7860"

try:
    with open(vits_config_path, "r", encoding="utf-8") as file:
        vits_data = json.load(file)
except Exception as e:
    print('加载配置文件失败，请进行修复')
    exit

# 加载说话人配置
speakers = vits_data["speakers"]

# 语言转音
def text_to_yin(text):
    # 如果是中文，则将其转换为拼音
    if '\u4e00' <= text <= '\u9fff':
        return ''.join(pypinyin.lazy_pinyin(text))
    
    # 如果是日语，则将其转换为罗马音
    elif 'ぁ' <= text <= 'ん' or 'ァ' <= text <= 'ヶ':
        kakasi = pykakasi.kakasi()
        kakasi.setMode("J","H")  # J(Kanji) to H(Hiragana)
        text_conv = kakasi.getConverter().do(text)
        return text_conv.lower()  # 转小写

    # 其他则默认为英文
    else:
        return text.lower()  # 转小写

# 将英文字符串打散为单个字符，并进行模拟按键操作和鼠标移动
def type_english(text):
    # print('type_english text=' + text)
    for char in text:
        pyautogui.typewrite(char)
    
    return

    # 将鼠标移动到屏幕上的随机位置
    screenWidth, screenHeight = pyautogui.size()
    randomX = random.randint(0, screenWidth)
    randomY = random.randint(0, screenHeight)
    # 持续时间为2秒
    pyautogui.moveTo(randomX, randomY, duration=2.0, tween=pyautogui.easeInOutCirc)  


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


room_id = int(input("请输入直播间编号: "))  # 输入直播间编号
room = live.LiveDanmaku(room_id)  # 连接弹幕服务器

@room.on('DANMU_MSG')  # 弹幕消息事件回调函数
async def on_danmaku(event):
    """
    处理弹幕消息
    :param event: 弹幕消息事件
    """
    content = event["data"]["info"][1]  # 获取弹幕内容
    user_name = event["data"]["info"][2][1]  # 获取用户昵称
    print(f"[{user_name}]: {content}")  # 打印弹幕信息

    # 原版的AI语音合成
    # command = f'edge-tts --voice zh-CN-XiaoyiNeural --text "{content}" --write-media output.mp3'  # 将 AI 生成的文本传递给 edge-tts 命令
    # subprocess.run(command, shell=True)  # 执行命令行指令

    # with open("./output.txt", "a", encoding="utf-8") as f:
    #     f.write(f"[AI回复{user_name}]：{content}\n")  # 将回复写入文件

    # character = "ikaros"
    character = "妮姆芙"
    language = "日语"
    text = "こんにちわ。"
    speed = 1

    text = content

    # 语言检测 一个是语言，一个是概率
    language, score = langid.classify(text)

    # 自定义语言名称（需要匹配请求解析）
    language_name_dict = {"en": "英语", "zh": "中文", "jp": "日语"}  

    if language in language_name_dict:
        language = language_name_dict[language]
    else:
        language = "日语"  # 无法识别出语言代码时的默认值

    # print("language=" + language)

    # 将英文字符串打散为单个字符，并进行模拟按键操作
    # 注意：需要管理员权限才能生效
    # 这个功能主要是为了配合live2d的按键检测动作使用的，不需要的可以直接注释
    # type_english(text_to_yin(text))

    # 调用接口合成语音
    data_json = await get_data(character, language, text, speed)

    # print(data_json)

    name = data_json["data"][1]["name"]
    # 请求文件地址获取返回形式
    # file_data = await get_file(name)

    command = 'mpv.exe -vo null ' + name  # 播放音频文件
    subprocess.run(command, shell=True)  # 执行命令行指令

sync(room.connect())  # 开始监听弹幕流

