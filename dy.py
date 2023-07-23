import websocket
import json, logging, os

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
        os._exit(0)


    def on_message(ws, message):
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


if __name__ == '__main__':
    start_server()
    