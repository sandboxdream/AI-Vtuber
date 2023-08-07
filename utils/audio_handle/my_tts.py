import json, logging
import aiohttp
from urllib.parse import urlencode

from utils.common import Common
from utils.logger import Configure_logger
from utils.config import Config

class MY_TTS:
    def __init__(self, config_path):
        self.common = Common()
        self.config = Config(config_path)

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)


    # 请求vits的api
    async def vits_api(self, data):
        try:
            # API地址 "http://127.0.0.1:23456/voice/vits"
            API_URL = data["api_ip_port"] + '/voice/vits'
            data_json = {
                "text": data["content"],
                "id": data["id"],
                "format": data["format"],
                "lang": "ja",
                "length": data["length"],
                "noise": data["noise"],
                "noisew": data["noisew"],
                "max": data["max"]
            }
            
            if data["lang"] == "中文" or data["lang"] == "汉语":
                data_json["lang"] = "zh"
            elif data["lang"] == "英文" or data["lang"] == "英语":
                data_json["lang"] = "en"
            elif data["lang"] == "韩文" or data["lang"] == "韩语":
                data_json["lang"] = "ko"
            else:
                data_json["lang"] = "ja"

            url = f"{API_URL}?{urlencode(data_json)}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response = await response.read()
                    # print(response)
                    voice_tmp_path = './out/vits_' + self.common.get_bj_time(4) + '.wav'
                    with open(voice_tmp_path, 'wb') as f:
                        f.write(response)
                    
                    return voice_tmp_path
        except aiohttp.ClientError as e:
            logging.error(f'vits请求失败: {e}')
        except Exception as e:
            logging.error(f'vits未知错误: {e}')
        
        return None
