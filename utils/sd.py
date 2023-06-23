import threading
import webuiapi
# from PIL import Image
import pyvirtualcam
import numpy as np
import time
import logging

from .common import Common
from .logger import Configure_logger


class SD:
    def __init__(self, data): 
        self.common = Common()

        # 日志文件路径
        file_path = "./log/log-" + self.common.get_bj_time(1) + ".txt"
        Configure_logger(file_path)

        self.new_img = None
        self.sd_config = data

        try:
            # 创建 API 客户端
            self.api = webuiapi.WebUIApi(host=data["ip"], port=data["port"])

            # 在单独的线程中更新虚拟摄像头
            threading.Thread(target=self.update_virtual_camera).start()
        except Exception as e:
            logging.error(e)

    def update_virtual_camera(self):
        # 创建虚拟摄像头
        with pyvirtualcam.Camera(width=512, height=512, fps=1) as cam:
            while True:
                if self.new_img is not None:
                    # 调整图像尺寸以匹配虚拟摄像头的分辨率
                    resized_img = self.new_img.resize((cam.width, cam.height))

                    # 将 PIL 图像转换为 numpy 数组并设置数据类型为 uint8
                    frame = np.array(resized_img)
                    frame = frame.astype(np.uint8)

                    # 将图像帧发送到虚拟摄像头
                    cam.send(frame)

                # 暂停一段时间
                time.sleep(0.1)  # 这里使用示例等待时间，可以根据需要进行调整


    def process_input(self, user_input):

        # 使用用户输入的文本作为 prompt 调用 API
        """
            prompt：主要文本提示，用于指定生成图像的主题或内容。
            negative_prompt：负面文本提示，用于指定与生成图像相矛盾或相反的内容。
            seed：随机种子，用于控制生成过程的随机性。可以设置一个整数值，以获得可重复的结果。
            styles：样式列表，用于指定生成图像的风格。可以包含多个风格，例如 ["anime", "portrait"]。
            cfg_scale：提示词相关性，无分类器指导信息影响尺度(Classifier Free Guidance Scale) -图像应在多大程度上服从提示词-较低的值会产生更有创意的结果。
            sampler_index：采样器索引，用于指定生成图像时使用的采样器。默认情况下，该参数为 None。
            steps：生成图像的步数，用于控制生成的精确程度。
            enable_hr：是否启用高分辨率生成。默认为 False。
            hr_scale：高分辨率缩放因子，用于指定生成图像的高分辨率缩放级别。
            hr_upscaler：高分辨率放大器类型，用于指定高分辨率生成的放大器类型。
            hr_second_pass_steps：高分辨率生成的第二次传递步数。
            hr_resize_x：生成图像的水平尺寸。
            hr_resize_y：生成图像的垂直尺寸。
            denoising_strength：去噪强度，用于控制生成图像中的噪点。
        """
        result = self.api.txt2img(prompt=user_input,
            negative_prompt=self.sd_config["negative_prompt"],
            seed=self.sd_config["seed"],
            styles=self.sd_config["styles"],
            cfg_scale=self.sd_config["cfg_scale"],
            # sampler_index='DDIM',
            steps=self.sd_config["steps"],
            enable_hr=self.sd_config["enable_hr"],
            hr_scale=self.sd_config["hr_scale"],
            # hr_upscaler=webuiapi.HiResUpscaler.Latent,
            hr_second_pass_steps=self.sd_config["hr_second_pass_steps"],
            hr_resize_x=self.sd_config["hr_resize_x"],
            hr_resize_y=self.sd_config["hr_resize_y"],
            denoising_strength=self.sd_config["denoising_strength"],
        )

        try:
            # 获取返回的图像
            img = result.image
            self.new_img = img
        except Exception as e:
            logging.error(e)
            return None

