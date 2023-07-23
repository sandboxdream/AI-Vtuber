import logging, os

# 导入所需的库
from bilibili_api import live, sync

from utils.common import Common
from utils.logger import Configure_logger
from utils.my_handle import My_handle

"""
	___ _                       
	|_ _| | ____ _ _ __ ___  ___ 
	 | || |/ / _` | '__/ _ \/ __|
	 | ||   < (_| | | | (_) \__ \
	|___|_|\_\__,_|_|  \___/|___/

"""

# 点火起飞
def start_server():
    common = Common()
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)

    my_handle = My_handle("config.json")
    if my_handle is None:
        logging.info("程序初始化失败！")
        os._exit(0)

    # 初始化 Bilibili 直播间
    room = live.LiveDanmaku(my_handle.get_room_id())

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
        user_name = event["data"]["data"]["uname"]

        logging.info(f"用户：{user_name} 进入直播间")

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
