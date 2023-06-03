import subprocess  # 导入子进程模块
from chatterbot import ChatBot  # 导入聊天机器人库
from bilibili_api import live, sync  # 导入bilibili直播API库

bot = ChatBot(
    'tieba',  # 聊天机器人名字
    database_uri='sqlite:///db.sqlite3'  # 数据库URI，数据库用于存储对话历史
)

#版权信息，就别删了吧
print("--------------------")
print("作者：Xzai")
print("QQ：2744601427")
print("--------------------")

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

    prompt = f"{content}"  # 设置观众提问
    response = bot.get_response(prompt)  # 生成回复

    print(f"[AI回复{user_name}]：{response}")  # 打印AI回复信息

    command = f'edge-tts --voice zh-CN-XiaoyiNeural --text "{response.text}" --write-media output.mp3'  # 将 AI 生成的文本传递给 edge-tts 命令
    subprocess.run(command, shell=True)  # 执行命令行指令

    with open("./output.txt", "a", encoding="utf-8") as f:
        f.write(f"[AI回复{user_name}]：{response}\n")  # 将回复写入文件

    command = 'mpv.exe -vo null output.mp3'  # 播放音频文件
    subprocess.run(command, shell=True)  # 执行命令行指令

sync(room.connect())  # 开始监听弹幕流
