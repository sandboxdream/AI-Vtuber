import logging, os
import threading
import schedule
import random

from functools import partial

# 导入所需的库
from bilibili_api import live, sync

from utils.common import Common
from utils.config import Config
from utils.logger import Configure_logger
from utils.my_handle import My_handle

"""
	___ _                       
	|_ _| | ____ _ _ __ ___  ___ 
	 | || |/ / _` | '__/ _ \/ __|
	 | ||   < (_| | | | (_) \__ \
	|___|_|\_\__,_|_|  \___/|___/

"""

config = None
common = None
my_handle = None
# last_liveroom_data = None
last_username_list = None

# 点火起飞
def start_server():
    global config, common, my_handle, last_username_list

    config_path = "config.json"

    common = Common()
    config = Config(config_path)
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)
  
    my_handle = My_handle(config_path)
    if my_handle is None:
        logging.info("程序初始化失败！")
        os._exit(0)


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
        content = random_copy

        # 根据变量的有无来进行数据替换
        if "{time}" in random_copy:
            content = random_copy.format(time=time)
        if "{user_num}" in random_copy:
            content = random_copy.format(user_num="N")
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
        global config

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

    # 初始化 Bilibili 直播间
    room = live.LiveDanmaku(my_handle.get_room_id())

    """
    DANMU_MSG: 用户发送弹幕
    SEND_GIFT: 礼物
    COMBO_SEND：礼物连击
    GUARD_BUY：续费大航海
    SUPER_CHAT_MESSAGE：醒目留言（SC）
    SUPER_CHAT_MESSAGE_JPN：醒目留言（带日语翻译？）
    WELCOME: 老爷进入房间
    WELCOME_GUARD: 房管进入房间
    NOTICE_MSG: 系统通知（全频道广播之类的）
    PREPARING: 直播准备中
    LIVE: 直播开始
    ROOM_REAL_TIME_MESSAGE_UPDATE: 粉丝数等更新
    ENTRY_EFFECT: 进场特效
    ROOM_RANK: 房间排名更新
    INTERACT_WORD: 用户进入直播间
    ACTIVITY_BANNER_UPDATE_V2: 好像是房间名旁边那个xx小时榜
    本模块自定义事件：
    VIEW: 直播间人气更新
    ALL: 所有事件
    DISCONNECT: 断开连接（传入连接状态码参数）
    TIMEOUT: 心跳响应超时
    VERIFICATION_SUCCESSFUL: 认证成功
    """

    @room.on('DANMU_MSG')
    async def _(event):
        """
        处理直播间弹幕事件
        :param event: 弹幕事件数据
        """
        content = event["data"]["info"][1]  # 获取弹幕内容
        user_name = event["data"]["info"][2][1]  # 获取发送弹幕的用户昵称

        logging.info(f"[{user_name}]: {content}")

        data = {
            "username": user_name,
            "content": content
        }

        my_handle.process_data(data, "commit")

    @room.on('COMBO_SEND')
    async def _(event):
        """
        处理直播间礼物连击事件
        :param event: 礼物连击事件数据
        """

        gift_name = event["data"]["data"]["gift_name"]
        user_name = event["data"]["data"]["uname"]
        # 礼物数量
        combo_num = event["data"]["data"]["combo_num"]
        # 总金额
        combo_total_coin = event["data"]["data"]["combo_total_coin"]

        logging.info(f"用户：{user_name} 赠送 {combo_num} 个 {gift_name}，总计 {combo_total_coin}电池")

        data = {
            "gift_name": gift_name,
            "username": user_name,
            "num": combo_num,
            "unit_price": combo_total_coin / combo_num / 1000,
            "total_price": combo_total_coin / 1000
        }

        my_handle.process_data(data, "gift")

    @room.on('SEND_GIFT')
    async def _(event):
        """
        处理直播间礼物事件
        :param event: 礼物事件数据
        """

        # print(event)

        gift_name = event["data"]["data"]["giftName"]
        user_name = event["data"]["data"]["uname"]
        # 礼物数量
        num = event["data"]["data"]["num"]
        # 总金额
        combo_total_coin = event["data"]["data"]["combo_total_coin"]
        # 单个礼物金额
        discount_price = event["data"]["data"]["discount_price"]

        logging.info(f"用户：{user_name} 赠送 {num} 个 {gift_name}，单价 {discount_price}电池，总计 {combo_total_coin}电池")

        data = {
            "gift_name": gift_name,
            "username": user_name,
            "num": num,
            "unit_price": discount_price / 1000,
            "total_price": combo_total_coin / 1000
        }

        my_handle.process_data(data, "gift")

    @room.on('GUARD_BUY')
    async def _(event):
        """
        处理直播间续费大航海事件
        :param event: 续费大航海事件数据
        """

        logging.info(event)

    @room.on('SUPER_CHAT_MESSAGE')
    async def _(event):
        """
        处理直播间醒目留言（SC）事件
        :param event: 醒目留言（SC）事件数据
        """
        message = event["data"]["data"]["message"]
        uname = event["data"]["data"]["user_info"]["uname"]
        price = event["data"]["data"]["price"]

        logging.info(f"用户：{uname} 发送 {price}元 SC：{message}")

        data = {
            "gift_name": "SC",
            "username": uname,
            "num": 1,
            "unit_price": price,
            "total_price": price,
            "content": message
        }

        my_handle.process_data(data, "gift")

        my_handle.process_data(data, "commit")
        

    @room.on('INTERACT_WORD')
    async def _(event):
        """
        处理直播间用户进入直播间事件
        :param event: 用户进入直播间事件数据
        """
        global last_username_list

        user_name = event["data"]["data"]["uname"]

        logging.info(f"用户：{user_name} 进入直播间")

        # 添加用户名到最新的用户名列表
        add_username_to_last_username_list(user_name)

        data = {
            "username": user_name,
            "content": "进入直播间"
        }

        my_handle.process_data(data, "entrance")

    # @room.on('WELCOME')
    # async def _(event):
    #     """
    #     处理直播间老爷进入房间事件
    #     :param event: 老爷进入房间事件数据
    #     """

    #     print(event)

    # @room.on('WELCOME_GUARD')
    # async def _(event):
    #     """
    #     处理直播间房管进入房间事件
    #     :param event: 房管进入房间事件数据
    #     """

    #     print(event)


    try:
        # 启动 Bilibili 直播间连接
        sync(room.connect())
    except KeyboardInterrupt:
        logging.warning('程序被强行退出')
    finally:
        logging.warning('关闭连接...')
        os._exit(0)


if __name__ == '__main__':
    start_server()
