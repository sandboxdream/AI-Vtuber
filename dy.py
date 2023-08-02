import websocket
import json, logging, os
import time
import threading
import schedule
import random

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
            time = f"凌晨{hour}点"
        elif 6 <= hour and hour < 9:
            time = f"早晨{hour}点"
        elif 9 <= hour and hour < 12:
            time = f"上午{hour}点"
        elif hour == 12:
            time = f"中午{hour}点"
        elif 13 <= hour and hour < 18:
            time = f"下午{hour - 12}点"
        elif 18 <= hour and hour < 20:
            time = f"傍晚{hour - 12}点"
        elif 20 <= hour and hour < 24:
            time = f"晚上{hour - 12}点"


        # 根据对应索引从列表中随机获取一个值
        random_copy = random.choice(config.get("schedule")[index]["copy"])
        content = random_copy

        # 根据变量的有无来进行数据替换
        if "{time}" in random_copy:
            content = random_copy.format(time=time)
        if "{user_num}" in random_copy:
            content = random_copy.format(user_num=last_liveroom_data["OnlineUserCount"])
        if "{last_username}" in random_copy:
            content = random_copy.format(last_username=last_username_list[-1])

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

    def on_message(ws, message):
        global last_liveroom_data, last_username_list

        message_json = json.loads(message)
        # logging.debug(message_json)
        if "Type" in message_json:
            type = message_json["Type"]
            data_json = json.loads(message_json["Data"])
            
            if type == 1:
                user_name = data_json["User"]["Nickname"]
                content = data_json["Content"]
                
                logging.info(f'[📧直播间弹幕消息] [{user_name}]：{content}')

                data = {
                    "username": user_name,
                    "content": content
                }
                
                my_handle.process_data(data, "commit")

                pass

            elif type == 2:
                user_name = data_json["User"]["Nickname"]
                count = data_json["Count"]

                logging.info(f'[👍直播间点赞消息] {user_name} 点了{count}赞')                

            elif type == 3:
                user_name = data_json["User"]["Nickname"]

                logging.info(f'[🚹🚺直播间成员加入消息] 欢迎 {user_name} 进入直播间')

                data = {
                    "username": user_name,
                    "content": "进入直播间"
                }

                # 添加用户名到最新的用户名列表
                add_username_to_last_username_list(user_name)

                my_handle.process_data(data, "entrance")

            elif type == 4:
                logging.info(f'[➕直播间关注消息] 感谢 {data_json["User"]["Nickname"]} 的关注')

                pass

            elif type == 5:
                gift_name = data_json["GiftName"]
                user_name = data_json["User"]["Nickname"]
                # 礼物数量
                num = data_json["GiftCount"]
                # 礼物重复数量
                repeat_count = data_json["RepeatCount"]

                try:
                    # 暂时是写死的
                    data_path = "data/抖音礼物价格表.json"

                    # 读取JSON文件
                    with open(data_path, "r", encoding="utf-8") as file:
                        # 解析JSON数据
                        data_json = json.load(file)

                    if gift_name in data_json:
                        # 单个礼物金额 需要自己维护礼物价值表
                        discount_price = data_json[gift_name]
                    else:
                        logging.warning(f"数据文件：{data_path} 中，没有 {gift_name} 对应的价值，请手动补充数据")
                        discount_price = 1
                except Exception as e:
                    logging.error(e)
                    discount_price = 1


                # 总金额
                combo_total_coin = repeat_count * discount_price

                logging.info(f'[🎁直播间礼物消息] 用户：{user_name} 赠送 {num} 个 {gift_name}，单价 {discount_price}抖币，总计 {combo_total_coin}抖币')

                data = {
                    "gift_name": gift_name,
                    "username": user_name,
                    "num": num,
                    "unit_price": discount_price / 10,
                    "total_price": combo_total_coin / 10
                }

                my_handle.process_data(data, "gift")

            elif type == 6:
                logging.info(f'[直播间数据] {data_json["Content"]}')
                # {'OnlineUserCount': 50, 'TotalUserCount': 22003, 'TotalUserCountStr': '2.2万', 'OnlineUserCountStr': '50', 
                # 'MsgId': 7260517442466662207, 'User': None, 'Content': '当前直播间人数 50，累计直播间人数 2.2万', 'RoomId': 7260415920948906807}
                # print(f"data_json={data_json}")

                last_liveroom_data = data_json

                pass

            elif type == 8:
                logging.info(f'[分享直播间] 感谢 {data_json["User"]["Nickname"]} 分享了直播间')

                pass

    def on_error(ws, error):
        logging.error("Error:", error)

    def on_close(ws):
        logging.debug("WebSocket connection closed")

    def on_open(ws):
        logging.debug("WebSocket connection established")
        


    try: 
        # WebSocket连接URL
        ws_url = "ws://127.0.0.1:8888"

        logging.info(f"监听地址：{ws_url}")

        # 不设置日志等级
        websocket.enableTrace(False)
        # 创建WebSocket连接
        ws = websocket.WebSocketApp(ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open)

        # 运行WebSocket连接
        ws.run_forever()
    except KeyboardInterrupt:
        logging.warning('程序被强行退出')
    finally:
        logging.info('关闭连接...可能是直播间不存在或下播或网络问题')
        os._exit(0)

    # 等待子线程结束
    schedule_thread.join()


if __name__ == '__main__':
    start_server()
    