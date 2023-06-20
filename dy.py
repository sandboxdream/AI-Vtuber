import websocket
import json, logging

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
        logging.error("程序初始化失败！")
        exit(0)


    # 设置根日志记录器的等级
    logging.basicConfig(level=logging.WARNING)

    # 创建日志记录器
    logger = logging.getLogger(__name__)

    # 设置日志记录器的等级
    logger.setLevel(logging.INFO)


    def on_message(ws, message):
        message_json = json.loads(message)
        logging.debug(message_json)
        if "Type" in message_json:
            type = message_json["Type"]
            data_json = json.loads(message_json["Data"])
            
            if type == 1:
                user_name = data_json["User"]["Nickname"]
                content = data_json["Content"]
                
                logging.info(f'[📧直播间弹幕消息] [{user_name}]：{content}')
                
                my_handle.commit_handle(user_name, content)

                pass

            elif type == 2:
                logging.debug(f'[👍直播间点赞消息] {data_json["User"]["Nickname"]} 点赞了直播间')

                pass
                

            elif type == 3:
                logging.debug(f'[🚹🚺直播间成员加入消息] 欢迎 {data_json["User"]["Nickname"]} 进入直播间')

                pass

            elif type == 4:
                logging.debug(f'[➕直播间关注消息] 感谢 {data_json["User"]["Nickname"]} 的关注')

                pass

            elif type == 6:
                logging.debug(f'[直播间数据] {data_json["Content"]}')

                pass

            elif type == 8:
                logging.debug(f'[分享直播间] 感谢 {data_json["User"]["Nickname"]} 分享了直播间')

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

        logging.debug(f"监听地址：{ws_url}")

        # 创建WebSocket连接
        websocket.enableTrace(True)
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
        exit(0)
