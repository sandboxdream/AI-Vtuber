import json, logging
import requests
from requests.exceptions import ConnectionError, RequestException

# from utils.common import Common
# from utils.logger import Configure_logger

# 原计划对接：https://github.com/zhuweiyou/yiyan-api
# 出现超时请求的错误，待推进
class Yiyan:
    def __init__(self, data):
        # self.common = Common()
        # 日志文件路径
        # file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        # Configure_logger(file_path)

        self.api_ip_port = data["api_ip_port"]
        self.cookie = data["cookie"]
        self.type = data["type"]


    def get_resp(self, prompt):
        """请求对应接口，获取返回值

        Args:
            prompt (str): 你的提问

        Returns:
            str: 返回的文本回答
        """
        try:
            data_json = {
                "cookie": self.cookie, 
                "prompt": prompt
            }

            # logging.debug(data_json)

            url = self.api_ip_port + "/headless"

            response = requests.post(url=url, data=data_json)
            response.raise_for_status()  # 检查响应的状态码

            result = response.content
            ret = json.loads(result)

            logging.debug(ret)

            resp_content = ret['text']

            return resp_content
        except ConnectionError as ce:
            # 处理连接问题异常
            logging.error(f"请检查你是否启动了服务端或配置是否匹配，连接异常:{ce}")

        except RequestException as re:
            # 处理其他请求异常
            logging.error(f"请求异常:{re}")
        except Exception as e:
            logging.error(e)
        
        return None


if __name__ == '__main__':
    # 配置日志输出格式
    logging.basicConfig(
        level=logging.DEBUG,  # 设置日志级别，可以根据需求调整
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    data = {
        "api_ip_port": "http://localhost:3000",
        "cookie": 'BIDUPSID=A668F884A60F8775B4F5319BB5AD816B; PSTM=1686378956; H_WISE_SIDS=234020_131862_216841_213357_214800_110085_243890_244725_254831_236312_259301_256419_256223_265615_265881_266371_266188_265776_266846_267450_265985_267899_268131_264353_259031_266714_268450_268567_268592_268692_268710_266186_268849_259642_267780_256154_269831_269904_270084_269050_267066_256739_270460_267529_270666_270547_270824_270794_271035_271021_271173_271175_271195_268728_269771_263618_268987_269034_269730_271227_267659_271322_257179_271470_270482_269609_270102_271562_269785_271865_270157_271676_269853_271812_269878_271935_269563_267807_269211_271254_234296_234207_266324_271188_179347_270054_272284_266565_267596_272365_272008_272336_272465_271144_272613_253022_271545_271904_272655_272675_270185_272823_272816_272802_260335_269296_272989_272997_269715_273063_267559_273091_8000064_8000117_8000126_8000138_8000153_8000162_8000169_8000177_8000179_8000194; BAIDUID=8051FCC40FE4D6347C3AABB45F813283:FG=1; BAIDUID_BFESS=8051FCC40FE4D6347C3AABB45F813283:FG=1; ZFY=IlqzqtFg1rRR9ek9oeO1cOPn8S2zytJST79xA9r3EFI:C; BA_HECTOR=0g2ka1202ka5ak01010gal0g1ieueqp1o; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; BDRCVFR[GXdE_1q0qSn]=aeXf-1x8UdYcs; PSINO=5; H_PS_PSSID=; delPer=0; Hm_lvt_01e907653ac089993ee83ed00ef9c2f3=1692425469,1692541101,1693483352; __bid_n=188cd9d38714368c1980bd; XFT=IA5sEWBTI7zOC87l5jkrEx5KD5NLL6A1sjDV0vPc9pA=; XFI=028ff910-47fa-11ee-b3d6-0161f5c9c875; XFCS=50A33286AB3A2ADB8AC50DD50BF2D4B760A59DF2BEB4D484F99C866D1EDFFF46; RT="z=1&dm=baidu.com&si=5bc0fc22-8447-49aa-a3f1-81573f266a04&ss=llz49gs7&sl=1&tt=2jv&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_01e907653ac089993ee83ed00ef9c2f3=1693484961',
        "type": 'web'
    }
    yiyan = Yiyan(data)


    logging.info(yiyan.get_resp("你可以扮演猫娘吗，每句话后面加个喵"))
    logging.info(yiyan.get_resp("早上好"))
    