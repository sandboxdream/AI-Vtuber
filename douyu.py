import asyncio
import websockets
import json, logging, os
import time
import threading
import schedule
import random
import traceback

from functools import partial

from utils.common import Common
from utils.logger import Configure_logger
from utils.my_handle import My_handle
from utils.config import Config


config = None
common = None
my_handle = None
last_liveroom_data = None
last_username_list = None


def start_server():
    global config, common, my_handle, last_liveroom_data, last_username_list

    config_path = "config.json"

    config = Config(config_path)
    common = Common()
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)

    # 最新的直播间数据
    last_liveroom_data = {
        'OnlineUserCount': 0, 
        'TotalUserCount': 0, 
        'TotalUserCountStr': '0', 
        'OnlineUserCountStr': '0', 
        'MsgId': 0, 
        'User': None, 
        'Content': '当前直播间人数 0，累计直播间人数 0', 
        'RoomId': 0
    }
    # 最新入场的用户名列表
    last_username_list = [""]

    my_handle = My_handle(config_path)
    if my_handle is None:
        logging.error("程序初始化失败！")
        os._exit(0)


    # 添加用户名到最新的用户名列表
    def add_username_to_last_username_list(data):
        global last_username_list

        # 添加数据到 最新入场的用户名列表
        last_username_list.append(data)
        
        # 保留最新的3个数据
        last_username_list = last_username_list[-3:]


    # 定时任务
    def schedule_task(index):
        global config, common, my_handle, last_liveroom_data, last_username_list

        logging.debug("定时任务执行中...")
        hour, min = common.get_bj_time(6)

        if 0 <= hour and hour < 6:
            time = f"凌晨{hour}点{min}分"
        elif 6 <= hour and hour < 9:
            time = f"早晨{hour}点{min}分"
        elif 9 <= hour and hour < 12:
            time = f"上午{hour}点{min}分"
        elif hour == 12:
            time = f"中午{hour}点{min}分"
        elif 13 <= hour and hour < 18:
            time = f"下午{hour - 12}点{min}分"
        elif 18 <= hour and hour < 20:
            time = f"傍晚{hour - 12}点{min}分"
        elif 20 <= hour and hour < 24:
            time = f"晚上{hour - 12}点{min}分"


        # 根据对应索引从列表中随机获取一个值
        random_copy = random.choice(config.get("schedule")[index]["copy"])

        # 假设有多个未知变量，用户可以在此处定义动态变量
        variables = {
            'time': time,
            'user_num': "N",
            'last_username': last_username_list[-1],
        }

        # 使用字典进行字符串替换
        if any(var in random_copy for var in variables):
            content = random_copy.format(**{var: value for var, value in variables.items() if var in random_copy})
        else:
            content = random_copy

        data = {
            "username": None,
            "content": content
        }

        logging.info(f"定时任务：{content}")

        my_handle.process_data(data, "schedule")


    # 启动定时任务
    def run_schedule():
        try:
            for index, task in enumerate(config.get("schedule")):
                if task["enable"]:
                    # print(task)
                    # 设置定时任务，每隔n秒执行一次
                    schedule.every(task["time"]).seconds.do(partial(schedule_task, index))
        except Exception as e:
            logging.error(e)

        while True:
            schedule.run_pending()
            # time.sleep(1)  # 控制每次循环的间隔时间，避免过多占用 CPU 资源


    # 创建定时任务子线程并启动
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.start()


    # 启动动态文案
    async def run_trends_copywriting():
        global config

        try:
            if False == config.get("trends_copywriting", "enable"):
                return
            
            logging.info(f"动态文案任务线程运行中...")

            while True:
                # 文案文件路径列表
                copywriting_file_path_list = []

                # 获取动态文案列表
                for copywriting in config.get("trends_copywriting", "copywriting"):
                    # 获取文件夹内所有文件的文件绝对路径，包括文件扩展名
                    for tmp in common.get_all_file_paths(copywriting["folder_path"]):
                        copywriting_file_path_list.append(tmp)

                    # 是否开启随机播放
                    if config.get("trends_copywriting", "random_play"):
                        random.shuffle(copywriting_file_path_list)

                    # 遍历文案文件路径列表  
                    for copywriting_file_path in copywriting_file_path_list:
                        # 获取文案文件内容
                        copywriting_file_content = common.read_file_return_content(copywriting_file_path)
                        # 是否启用提示词对文案内容进行转换
                        if copywriting["prompt_change_enable"]:
                            data_json = {
                                "user_name": "trends_copywriting",
                                "content": copywriting["prompt_change_content"] + copywriting_file_content
                            }

                            # 调用函数进行LLM处理，以及生成回复内容，进行音频合成，需要好好考虑考虑实现
                            data_json["content"] = my_handle.llm_handle(config.get("chat_type"), data_json)
                        else:
                            data_json = {
                                "user_name": "trends_copywriting",
                                "content": copywriting_file_content
                            }

                        # 空数据判断
                        if data_json["content"] != None and data_json["content"] != "":
                            # 发给直接复读进行处理
                            my_handle.reread_handle(data_json)

                            await asyncio.sleep(config.get("trends_copywriting", "play_interval"))
        except Exception as e:
            logging.error(traceback.format_exc())


    # 创建动态文案子线程并启动
    threading.Thread(target=lambda: asyncio.run(run_trends_copywriting())).start()



    async def on_message(websocket, path):
        global last_liveroom_data, last_username_list

        async for message in websocket:
            # print(f"收到消息: {message}")
            # await websocket.send("服务器收到了你的消息: " + message)

            try:
                data_json = json.loads(message)
                # logging.debug(data_json)
                if data_json["type"] == "comment":
                    # logging.info(data_json)

                    user_name = data_json["username"]
                    content = data_json["content"]
                    
                    logging.info(f'[📧直播间弹幕消息] [{user_name}]：{content}')

                    data = {
                        "username": user_name,
                        "content": content
                    }
                    
                    my_handle.process_data(data, "comment")

                    # 添加用户名到最新的用户名列表
                    add_username_to_last_username_list(user_name)

            except Exception as e:
                logging.error(e)
                logging.error("数据解析错误！")
                continue
        

    async def ws_server():
        ws_url = "127.0.0.1"
        ws_port = 5000
        server = await websockets.serve(on_message, ws_url, ws_port)
        logging.info(f"WebSocket 服务器已在 {ws_url}:{ws_port} 启动")
        await server.wait_closed()


    asyncio.run(ws_server())


if __name__ == '__main__':
    start_server()