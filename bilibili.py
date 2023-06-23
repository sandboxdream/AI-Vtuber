import logging

# 导入所需的库
from bilibili_api import live, sync


from utils.common import Common
from utils.logger import Configure_logger
from utils.my_handle import My_handle

def start_server():
    common = Common()
    # 日志文件路径
    log_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(log_path)
    
    my_handle = My_handle("config.json")
    if my_handle is None:
        logging.info("程序初始化失败！")
        exit(0)


    # 初始化 Bilibili 直播间
    room = live.LiveDanmaku(my_handle.get_room_id())


    @room.on('DANMU_MSG')
    async def on_danmaku(event):
        """
        处理直播间弹幕事件
        :param event: 弹幕事件数据
        """
        content = event["data"]["info"][1]  # 获取弹幕内容
        user_name = event["data"]["info"][2][1]  # 获取发送弹幕的用户昵称

        my_handle.commit_handle(user_name, content)


    try: 
        # 启动 Bilibili 直播间连接
        sync(room.connect())
    except KeyboardInterrupt:
        logging.warning('程序被强行退出')
    finally:
        logging.warning('关闭连接...')
        exit(0)


if __name__ == '__main__':
    start_server()