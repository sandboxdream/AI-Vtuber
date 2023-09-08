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
        "cookie": 'BIDUPSID=A668F884A60F8775B4F5319BB5AD816B; PSTM=1686378956; BAIDUID=8051FCC40FE4D6347C3AABB45F813283:FG=1; BAIDUID_BFESS=8051FCC40FE4D6347C3AABB45F813283:FG=1; ZFY=IlqzqtFg1rRR9ek9oeO1cOPn8S2zytJST79xA9r3EFI:C; __bid_n=188cd9d38714368c1980bd; ET_WHITELIST=etwhitelistintwodays; BA_HECTOR=a1al0100a0200ga0a1ag0gaj1if5e8s1o; H_WISE_SIDS=216853_213352_214792_110085_244720_254831_261710_236312_256419_265881_266360_265615_267074_259031_268478_268593_266187_259642_269401_269778_269832_269904_267066_256739_270460_270535_270516_270547_270922_271036_271020_271170_271174_269771_263618_267659_271321_265034_271272_266028_270102_271560_271726_270443_271869_270157_271674_269858_271812_269878_271954_268758_267804_269665_271255_234296_234207_271187_272223_272284_272364_272008_272458_253022_269729_272741_272822_272841_272802_260335_269297_271285_267596_273061_267560_273090_273161_273118_273136_273240_273301_273400_271158_270055_271146_273671_273704_264170_270186_270142_274080_273932_273965_274141_274177_269610_274207_273917_274233_273786_273043_273598_263750_272805_272319_272560_274425_274422_272332_197096; BDRCVFR[GXdE_1q0qSn]=aeXf-1x8UdYcs; PSINO=5; H_PS_PSSID=; delPer=0; BDORZ=FFFB88E999055A3F8A630C64834BD6D0; Hm_lvt_01e907653ac089993ee83ed00ef9c2f3=1692425469,1692541101,1693483352,1693709742; XFT=u5oY8QNaQLR3vAsRd1CEydt/e9bf8brrvvynvl4G0y4=; XFI=6fe9cfb0-4a05-11ee-9d92-b7e0d2a9a0cb; XFCS=3DF06024E37B44A58BEF2BE93646805739B8C4AD6A31852915AAE1659CA635D7; RT="z=1&dm=baidu.com&si=5bc0fc22-8447-49aa-a3f1-81573f266a04&ss=lm2v1sa2&sl=2&tt=2cl&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf"; Hm_lpvt_01e907653ac089993ee83ed00ef9c2f3=1693709771', 
        "type": 'web'
    }
    yiyan = Yiyan(data)


    logging.info(yiyan.get_resp("你可以扮演猫娘吗，每句话后面加个喵"))
    logging.info(yiyan.get_resp("早上好"))
    