import sys, os, json, subprocess, importlib, re
import logging
import time
# from functools import partial

from utils.config import Config

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QComboBox, QLineEdit, QTextEdit
from PyQt5.QtGui import QFont, QDesktopServices, QIcon
from PyQt5.QtCore import QTimer, QThread, QEventLoop, pyqtSignal, QUrl

import http.server
import socketserver

import UI_main

from utils.common import Common
from utils.logger import Configure_logger



class AI_VTB(QMainWindow):
    proxy = None
    # proxy = {
    #     "http": "http://127.0.0.1:10809",
    #     "https": "http://127.0.0.1:10809"
    # }

    # 线程
    my_thread = None
    
    '''
        初始化
    '''
    def __init__(self):
        logging.info("程序开始运行")
        
        self.app = QApplication(sys.argv)
        super().__init__()
        self.ui = UI_main.Ui_MainWindow()
        self.ui.setupUi(self)

        # 获取显示器分辨率
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.screenheight = self.screenRect.height()
        self.screenwidth = self.screenRect.width()

        logging.debug("Screen height {}".format(self.screenheight))
        logging.debug("Screen width {}".format(self.screenwidth))

        self.height = int(self.screenheight * 0.7)
        self.width = int(self.screenwidth * 0.7)

        # 设置软件图标
        app_icon = QIcon("ui/icon.png")
        self.setWindowIcon(app_icon)

        # self.resize(self.width, self.height)

        # 设置实例
        self.CreateItems()
        # 读取配置文件 进行初始化
        self.init_config()
        # 初始化
        self.init_ui()


    # 设置实例 
    def CreateItems(self):
        # 定时器
        self.timer = QTimer(self)
        self.eventLoop = QEventLoop(self)

        # self.timer_connection = None
    

    # 读取配置文件 进行初始化(开始堆shi喵)
    def init_config(self):
        global config, config_path

        # 如果配置文件不存在，创建一个新的配置文件
        if not os.path.exists(config_path):
            logging.error("配置文件不存在！！！请恢复")
            self.show_message_box("错误", f"配置文件不存在！！！请恢复", QMessageBox.Critical)
            exit(0)
            

        config = Config(config_path)

        try:
            
            # 设置会话初始值
            self.session_config = {'msg': [{"role": "system", "content": config.get('chatgpt', 'preset')}]}
            self.sessions = {}
            self.current_key_index = 0

            self.platform = config.get("platform")
            
            # 直播间号
            self.room_id = config.get("room_display_id")

            self.before_prompt = config.get("before_prompt")
            self.after_prompt = config.get("after_prompt")

            self.commit_log_type = config.get("commit_log_type")

            # 过滤配置
            self.filter_config = config.get("filter")

            self.chat_type = config.get("chat_type")

            self.need_lang = config.get("need_lang")

            self.live2d_config = config.get("live2d")

            # openai
            self.openai_config = config.get("openai")
            # chatgpt
            self.chatgpt_config = config.get("chatgpt")
            # claude
            self.claude_config = config.get("claude")
            # chatterbot
            self.chatterbot_config = config.get("chatterbot")
            # langchain_pdf
            self.langchain_pdf_config = config.get("langchain_pdf")
            # chatglm
            self.chatglm_config = config.get("chatglm")
            # langchain_pdf_local
            self.langchain_pdf_local_config = config.get("langchain_pdf_local")
            

            # 音频合成使用技术
            self.audio_synthesis_type = config.get("audio_synthesis_type")

            self.edge_tts_config = config.get("edge-tts")
            self.vits_config = config.get("vits")
            self.elevenlabs_config = config.get("elevenlabs")
            
            self.sd_config = config.get("sd")

            self.header_config = config.get("header")

            """
                配置Label提示
            """
            # 设置鼠标悬停时的提示文本
            self.ui.label_platform.setToolTip("运行的平台版本")  
            self.ui.label_room_display_id.setToolTip("待监听的直播间的房间号（直播间URL最后一个/后的数字和字母），需要是开播状态")
            self.ui.label_chat_type.setToolTip("弹幕对接的聊天类型")
            self.ui.label_need_lang.setToolTip("只回复选中语言的弹幕，其他语言将被过滤")
            self.ui.label_before_prompt.setToolTip("提示词前缀，会自带追加在弹幕前，主要用于追加一些特殊的限制")
            self.ui.label_after_prompt.setToolTip("提示词后缀，会自带追加在弹幕后，主要用于追加一些特殊的限制")
            self.ui.label_commit_log_type.setToolTip("弹幕日志类型，用于记录弹幕触发时记录的内容，默认只记录回答，降低当用户使用弹幕日志显示在直播间时，因为用户的不良弹幕造成直播间被封禁问题")

            self.ui.label_filter_before_must_str.setToolTip("本地违禁词数据路径（你如果不需要，可以清空文件内容）")
            self.ui.label_filter_after_must_str.setToolTip("本地违禁词数据路径（你如果不需要，可以清空文件内容）")
            self.ui.label_filter_badwords_path.setToolTip("本地违禁词数据路径（你如果不需要，可以清空文件内容）")
            self.ui.label_filter_max_len.setToolTip("最长阅读的英文单词数（空格分隔）")
            self.ui.label_filter_max_char_len.setToolTip("最长阅读的字符数，双重过滤，避免溢出")

            self.ui.label_live2d_enable.setToolTip("启动web服务，用于加载本地Live2D模型")
            self.ui.label_live2d_port.setToolTip("web服务运行的端口号，默认：12345，范围:0-65535，没事不要乱改就好")

            self.ui.label_audio_synthesis_type.setToolTip("语音合成的类型")

            self.ui.label_openai_api.setToolTip("API请求地址，支持代理")
            self.ui.label_openai_api_key.setToolTip("API KEY，支持代理")
            self.ui.label_chatgpt_model.setToolTip("指定要使用的模型，可以去官方API文档查看模型列表")
            self.ui.label_chatgpt_temperature.setToolTip("控制生成文本的随机性。较高的温度值会使生成的文本更随机和多样化，而较低的温度值会使生成的文本更加确定和一致。")
            self.ui.label_chatgpt_max_tokens.setToolTip("限制生成回答的最大长度。")
            self.ui.label_chatgpt_top_p.setToolTip("也被称为 Nucleus采样。这个参数控制模型从累积概率大于一定阈值的令牌中进行采样。较高的值会产生更多的多样性，较低的值会产生更少但更确定的回答。")
            self.ui.label_chatgpt_presence_penalty.setToolTip("控制模型生成回答时对给定问题提示的关注程度。较高的存在惩罚值会减少模型对给定提示的重复程度，鼓励模型更自主地生成回答。")
            self.ui.label_chatgpt_frequency_penalty.setToolTip("控制生成回答时对已经出现过的令牌的惩罚程度。较高的频率惩罚值会减少模型生成已经频繁出现的令牌，以避免重复和过度使用特定词语。")
            self.ui.label_chatgpt_preset.setToolTip("用于指定一组预定义的设置，以便模型更好地适应特定的对话场景。")

            self.ui.label_claude_slack_user_token.setToolTip("Slack平台配置的用户Token，参考文档的Claude板块进行配置")
            self.ui.label_claude_bot_user_id.setToolTip("Slack平台添加的Claude显示的成员ID，参考文档的Claude板块进行配置")

            self.ui.label_chatglm_api_ip_port.setToolTip("ChatGLM的API版本运行后的服务链接（需要完整的URL）")
            self.ui.label_chatglm_max_length.setToolTip("生成回答的最大长度限制，以令牌数或字符数为单位。")
            self.ui.label_chatglm_top_p.setToolTip("也称为 Nucleus采样。控制模型生成时选择概率的阈值范围。")
            self.ui.label_chatglm_temperature.setToolTip("温度参数，控制生成文本的随机性。较高的温度值会产生更多的随机性和多样性。")
            
            self.ui.label_langchain_pdf_openai_api_key.setToolTip("官方OpenAI API KEY")
            self.ui.label_langchain_pdf_data_path.setToolTip("加载的本地pdf数据文件路径（到x.pdf）, 如：./data/伊卡洛斯百度百科.pdf")
            self.ui.label_langchain_pdf_separator.setToolTip("拆分文本的分隔符，这里使用 换行符 作为分隔符。")
            self.ui.label_langchain_pdf_chunk_size.setToolTip("每个文本块的最大字符数(文本块字符越多，消耗token越多，回复越详细)")
            self.ui.label_langchain_pdf_chunk_overlap.setToolTip("两个相邻文本块之间的重叠字符数。这种重叠可以帮助保持文本的连贯性，特别是当文本被用于训练语言模型或其他需要上下文信息的机器学习模型时")
            self.ui.label_langchain_pdf_model_name.setToolTip("指定要使用的OpenAI模型名称")
            self.ui.label_langchain_pdf_chain_type.setToolTip("指定要生成的语言链的类型，例如：stuff")
            self.ui.label_langchain_pdf_show_cost.setToolTip("表示是否显示生成文本的成本。如果启用，将在终端中显示成本信息。")

            self.ui.label_langchain_pdf_local_slack_user_token.setToolTip("Slack平台配置的用户Token，参考文档的Claude板块进行配置")
            self.ui.label_langchain_pdf_local_bot_user_id.setToolTip("Slack平台添加的Claude显示的成员ID，参考文档的Claude板块进行配置")
            self.ui.label_langchain_pdf_local_data_path.setToolTip("加载的本地pdf数据文件路径（到x.pdf）, 如：./data/伊卡洛斯百度百科.pdf")
            self.ui.label_langchain_pdf_local_separator.setToolTip("拆分文本的分隔符，这里使用 换行符 作为分隔符。")
            self.ui.label_langchain_pdf_local_chunk_size.setToolTip("每个文本块的最大字符数(文本块字符越多，消耗token越多，回复越详细)")
            self.ui.label_langchain_pdf_local_chunk_overlap.setToolTip("两个相邻文本块之间的重叠字符数。这种重叠可以帮助保持文本的连贯性，特别是当文本被用于训练语言模型或其他需要上下文信息的机器学习模型时")
            self.ui.label_langchain_pdf_local_embedding_model.setToolTip("指定要使用的OpenAI模型名称")
            self.ui.label_langchain_pdf_local_chain_type.setToolTip("指定要生成的语言链的类型，例如：stuff")
            self.ui.label_langchain_pdf_local_show_cost.setToolTip("表示是否显示生成文本的成本。如果启用，将在终端中显示成本信息。")

            self.ui.label_chatterbot_name.setToolTip("机器人名称")
            self.ui.label_chatterbot_db_path.setToolTip("数据库路径")

            self.ui.label_edge_tts_voice.setToolTip("选定的说话人(cmd执行：edge-tts -l 可以查看所有支持的说话人)")
            self.ui.label_edge_tts_rate.setToolTip("语速增益 默认是 +0%，可以增减，注意 + - %符合别搞没了，不然会影响语音合成")
            self.ui.label_edge_tts_volume.setToolTip("音量增益 默认是 +0%，可以增减，注意 + - %符合别搞没了，不然会影响语音合成")

            self.ui.label_vits_config_path.setToolTip("配置文件的路径，例如：E:\\inference\\finetune_speaker.json")
            self.ui.label_vits_api_ip_port.setToolTip("推理服务运行的链接（需要完整的URL）")
            self.ui.label_vits_character.setToolTip("选择的说话人，配置文件中的speaker中的其中一个")
            self.ui.label_vits_speed.setToolTip("语速，默认为1")

            self.ui.label_elevenlabs_api_key.setToolTip("elevenlabs密钥，可以不填，默认也有一定额度的免费使用权限，具体多少不知道")
            self.ui.label_elevenlabs_voice.setToolTip("选择的说话人名")
            self.ui.label_elevenlabs_model.setToolTip("选择的模型")

            self.ui.label_sd_enable.setToolTip("是否启用SD来进行画图")
            self.ui.label_sd_trigger.setToolTip("触发的关键词（弹幕头部触发）")
            self.ui.label_sd_ip.setToolTip("服务运行的IP地址")
            self.ui.label_sd_port.setToolTip("服务运行的端口")
            self.ui.label_sd_negative_prompt.setToolTip("负面文本提示，用于指定与生成图像相矛盾或相反的内容")
            self.ui.label_sd_seed.setToolTip("随机种子，用于控制生成过程的随机性。可以设置一个整数值，以获得可重复的结果。")
            self.ui.label_sd_styles.setToolTip("样式列表，用于指定生成图像的风格。可以包含多个风格，例如 [\"anime\", \"portrait\"]")
            self.ui.label_sd_cfg_scale.setToolTip("提示词相关性，无分类器指导信息影响尺度(Classifier Free Guidance Scale) -图像应在多大程度上服从提示词-较低的值会产生更有创意的结果。")
            self.ui.label_sd_steps.setToolTip("生成图像的步数，用于控制生成的精确程度。")
            self.ui.label_sd_enable_hr.setToolTip("是否启用高分辨率生成。默认为 False。")
            self.ui.label_sd_hr_scale.setToolTip("高分辨率缩放因子，用于指定生成图像的高分辨率缩放级别。")
            self.ui.label_sd_hr_second_pass_steps.setToolTip("高分辨率生成的第二次传递步数。")
            self.ui.label_sd_hr_resize_x.setToolTip("生成图像的水平尺寸。")
            self.ui.label_sd_hr_resize_y.setToolTip("生成图像的垂直尺寸。")
            self.ui.label_sd_denoising_strength.setToolTip("去噪强度，用于控制生成图像中的噪点。")

            self.ui.label_header_useragent.setToolTip("请求头，暂时没有用到，备用")


            """
                配置同步UI
            """
            # 修改下拉框内容
            self.ui.comboBox_platform.clear()
            self.ui.comboBox_platform.addItems(["哔哩哔哩", "抖音", "快手"])
            platform_index = 0
            if self.platform == "bilibili":
                platform_index = 0
            elif self.platform == "dy":
                platform_index = 1
            elif self.platform == "ks":
                platform_index = 2 
            self.ui.comboBox_platform.setCurrentIndex(platform_index)
            
            # 修改输入框内容
            self.ui.lineEdit_room_display_id.setText(self.room_id)
            
            self.ui.comboBox_chat_type.clear()
            self.ui.comboBox_chat_type.addItems(["复读机", "ChatGPT", "Claude", "ChatGLM", "Langchain_pdf", "Langchain_pdf+gpt", "Chatterbot", "Langchain_pdf_local"])
            chat_type_index = 0
            if self.chat_type == "none":
                chat_type_index = 0
            elif self.chat_type == "gpt":
                chat_type_index = 1
            elif self.chat_type == "claude":
                chat_type_index = 2 
            elif self.chat_type == "chatglm":
                chat_type_index = 3
            elif self.chat_type == "langchain_pdf":
                chat_type_index = 4
            elif self.chat_type == "langchain_pdf+gpt":
                chat_type_index = 5
            elif self.chat_type == "chatterbot":
                chat_type_index = 6
            elif self.chat_type == "langchain_pdf_local":
                chat_type_index = 7
            self.ui.comboBox_chat_type.setCurrentIndex(chat_type_index)
            
            self.ui.comboBox_need_lang.clear()
            self.ui.comboBox_need_lang.addItems(["所有", "中文", "英文", "日文"])
            need_lang_index = 0
            if self.need_lang == "none":
                need_lang_index = 0
            elif self.need_lang == "zh":
                need_lang_index = 1
            elif self.need_lang == "en":
                need_lang_index = 2
            elif self.need_lang == "jp":
                need_lang_index = 3
            self.ui.comboBox_need_lang.setCurrentIndex(need_lang_index)

            self.ui.lineEdit_before_prompt.setText(self.before_prompt)
            self.ui.lineEdit_after_prompt.setText(self.after_prompt)

            self.ui.comboBox_commit_log_type.clear()
            commit_log_types = ["问答", "问题", "回答", "不记录"]
            self.ui.comboBox_commit_log_type.addItems(commit_log_types)
            commit_log_type_index = commit_log_types.index(self.commit_log_type)
            self.ui.comboBox_commit_log_type.setCurrentIndex(commit_log_type_index)

            tmp_str = ""
            for tmp in self.filter_config['before_must_str']:
                tmp_str = tmp_str + tmp + "\n"
            self.ui.textEdit_filter_before_must_str.setText(tmp_str)
            tmp_str = ""
            for tmp in self.filter_config['after_must_str']:
                tmp_str = tmp_str + tmp + "\n"
            self.ui.textEdit_filter_after_must_str.setText(tmp_str)
            self.ui.lineEdit_filter_badwords_path.setText(self.filter_config['badwords_path'])
            self.ui.lineEdit_filter_max_len.setText(str(self.filter_config['max_len']))
            self.ui.lineEdit_filter_max_char_len.setText(str(self.filter_config['max_char_len']))

            if self.live2d_config['enable']:
                self.ui.checkBox_live2d_enable.setChecked(True)
            self.ui.lineEdit_live2d_port.setText(str(self.live2d_config['port']))

            self.ui.lineEdit_header_useragent.setText(self.header_config['userAgent'])

            self.ui.lineEdit_openai_api.setText(self.openai_config['api'])
            tmp_str = ""
            for tmp in self.openai_config['api_key']:
                tmp_str = tmp_str + tmp + "\n"
            self.ui.textEdit_openai_api_key.setText(tmp_str)

            self.ui.lineEdit_chatgpt_model.setText(self.chatgpt_config['model'])
            self.ui.lineEdit_chatgpt_temperature.setText(str(self.chatgpt_config['temperature']))
            self.ui.lineEdit_chatgpt_max_tokens.setText(str(self.chatgpt_config['max_tokens']))
            self.ui.lineEdit_chatgpt_top_p.setText(str(self.chatgpt_config['top_p']))
            self.ui.lineEdit_chatgpt_presence_penalty.setText(str(self.chatgpt_config['presence_penalty']))
            self.ui.lineEdit_chatgpt_frequency_penalty.setText(str(self.chatgpt_config['frequency_penalty']))
            self.ui.lineEdit_chatgpt_preset.setText(self.chatgpt_config['preset'])

            self.ui.lineEdit_claude_slack_user_token.setText(self.claude_config['slack_user_token'])
            self.ui.lineEdit_claude_bot_user_id.setText(self.claude_config['bot_user_id'])

            self.ui.lineEdit_chatglm_api_ip_port.setText(self.chatglm_config['api_ip_port'])
            self.ui.lineEdit_chatglm_max_length.setText(str(self.chatglm_config['max_length']))
            self.ui.lineEdit_chatglm_top_p.setText(str(self.chatglm_config['top_p']))
            self.ui.lineEdit_chatglm_temperature.setText(str(self.chatglm_config['temperature']))
            self.ui.lineEdit_langchain_pdf_model_name.setText(self.langchain_pdf_config['model_name'])
            self.ui.lineEdit_langchain_pdf_openai_api_key.setText(self.langchain_pdf_config['openai_api_key'])
            self.ui.lineEdit_langchain_pdf_data_path.setText(self.langchain_pdf_config['data_path'])
            self.ui.lineEdit_langchain_pdf_separator.setText(self.langchain_pdf_config['separator'])
            self.ui.lineEdit_langchain_pdf_chunk_size.setText(str(self.langchain_pdf_config['chunk_size']))
            self.ui.lineEdit_langchain_pdf_chunk_overlap.setText(str(self.langchain_pdf_config['chunk_overlap']))
            
            self.ui.lineEdit_langchain_pdf_chain_type.setText(self.langchain_pdf_config['chain_type'])
            if self.langchain_pdf_config['show_cost']:
                self.ui.checkBox_langchain_pdf_show_cost.setChecked(True)

            self.ui.lineEdit_langchain_pdf_local_slack_user_token.setText(self.langchain_pdf_local_config['slack_user_token'])
            self.ui.lineEdit_langchain_pdf_local_bot_user_id.setText(self.langchain_pdf_local_config['bot_user_id'])
            self.ui.lineEdit_langchain_pdf_local_data_path.setText(self.langchain_pdf_local_config['data_path'])
            self.ui.lineEdit_langchain_pdf_local_separator.setText(self.langchain_pdf_local_config['separator'])
            self.ui.lineEdit_langchain_pdf_local_chunk_size.setText(str(self.langchain_pdf_local_config['chunk_size']))
            self.ui.lineEdit_langchain_pdf_local_chunk_overlap.setText(str(self.langchain_pdf_local_config['chunk_overlap']))
            self.ui.comboBox_langchain_pdf_local_embedding_model.clear()
            self.ui.comboBox_langchain_pdf_local_embedding_model.addItems(["sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco", "GanymedeNil/text2vec-large-chinese"])
            langchain_pdf_local_embedding_model = 0
            if self.langchain_pdf_local_config['embedding_model'] == "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco":
                langchain_pdf_local_embedding_model = 0
            elif self.langchain_pdf_local_config['embedding_model'] == "GanymedeNil/text2vec-large-chinese":
                langchain_pdf_local_embedding_model = 1
            self.ui.comboBox_langchain_pdf_local_embedding_model.setCurrentIndex(langchain_pdf_local_embedding_model)
            self.ui.lineEdit_langchain_pdf_local_chain_type.setText(self.langchain_pdf_local_config['chain_type'])
            if self.langchain_pdf_local_config['show_cost']:
                self.ui.checkBox_langchain_pdf_local_show_cost.setChecked(True)

            self.ui.lineEdit_chatterbot_name.setText(self.chatterbot_config['name'])
            self.ui.lineEdit_chatterbot_db_path.setText(self.chatterbot_config['db_path'])

            self.ui.comboBox_audio_synthesis_type.clear()
            self.ui.comboBox_audio_synthesis_type.addItems(["Edge-TTS", "VITS-Fast", "elevenlabs"])
            audio_synthesis_type_index = 0
            if self.audio_synthesis_type == "edge-tts":
                audio_synthesis_type_index = 0
            elif self.audio_synthesis_type == "vits":
                audio_synthesis_type_index = 1
            elif self.audio_synthesis_type == "elevenlabs":
                audio_synthesis_type_index = 2 
            self.ui.comboBox_audio_synthesis_type.setCurrentIndex(audio_synthesis_type_index)

            self.ui.lineEdit_vits_config_path.setText(self.vits_config['config_path'])
            self.ui.lineEdit_vits_api_ip_port.setText(self.vits_config['api_ip_port'])
            self.ui.lineEdit_vits_character.setText(self.vits_config['character'])
            self.ui.lineEdit_vits_speed.setText(str(self.vits_config['speed']))

            self.ui.comboBox_edge_tts_voice.clear()
            with open('data\edge-tts-voice-list.txt', 'r') as file:
                file_content = file.read()
            # 按行分割内容，并去除每行末尾的换行符
            lines = file_content.strip().split('\n')
            # 存储到字符串数组中
            edge_tts_voices = [line for line in lines]
            # print(edge_tts_voices)
            self.ui.comboBox_edge_tts_voice.addItems(edge_tts_voices)
            edge_tts_voice_index = edge_tts_voices.index(self.edge_tts_config['voice'])
            self.ui.comboBox_edge_tts_voice.setCurrentIndex(edge_tts_voice_index)
            self.ui.lineEdit_edge_tts_rate.setText(self.edge_tts_config['rate'])
            self.ui.lineEdit_edge_tts_volume.setText(self.edge_tts_config['volume'])

            self.ui.lineEdit_elevenlabs_api_key.setText(self.elevenlabs_config['api_key'])
            self.ui.lineEdit_elevenlabs_voice.setText(self.elevenlabs_config['voice'])
            self.ui.lineEdit_elevenlabs_model.setText(self.elevenlabs_config['model'])

            # sd 配置回显部分
            if self.sd_config['enable']:
                self.ui.checkBox_sd_enable.setChecked(True)
            self.ui.lineEdit_sd_trigger.setText(self.sd_config['trigger'])
            self.ui.lineEdit_sd_ip.setText(self.sd_config['ip'])
            self.ui.lineEdit_sd_port.setText(str(self.sd_config['port']))
            self.ui.lineEdit_sd_negative_prompt.setText(self.sd_config['negative_prompt'])
            self.ui.lineEdit_sd_seed.setText(str(self.sd_config['seed']))
            tmp_str = ""
            for tmp in self.sd_config['styles']:
                tmp_str = tmp_str + tmp + "\n"
            self.ui.textEdit_sd_styles.setText(tmp_str)
            self.ui.lineEdit_sd_cfg_scale.setText(str(self.sd_config['cfg_scale']))
            self.ui.lineEdit_sd_steps.setText(str(self.sd_config['steps']))
            self.ui.lineEdit_sd_hr_resize_x.setText(str(self.sd_config['hr_resize_x']))
            self.ui.lineEdit_sd_hr_resize_y.setText(str(self.sd_config['hr_resize_y']))
            if self.sd_config['enable_hr']:
                self.ui.checkBox_sd_enable_hr.setChecked(True)
            self.ui.lineEdit_sd_hr_scale.setText(str(self.sd_config['hr_scale']))
            self.ui.lineEdit_sd_hr_second_pass_steps.setText(str(self.sd_config['hr_second_pass_steps']))
            self.ui.lineEdit_sd_denoising_strength.setText(str(self.sd_config['denoising_strength']))
            
            # 显隐各板块
            self.oncomboBox_chat_type_IndexChanged(chat_type_index)
            self.oncomboBox_audio_synthesis_type_IndexChanged(audio_synthesis_type_index)

            logging.info("配置文件加载成功。")
        except Exception as e:
            logging.info(e)
            return None
    
    
    # ui初始化
    def init_ui(self):
        # 统一设置下样式先
        common_css = "margin: 5px 0px; height: 40px;"

        # 无效设置
        font = QFont("微软雅黑", 14)  # 创建一个字体对象
        font.setWeight(QFont.Bold)  # 设置字体粗细

        labels = self.findChildren(QLabel)
        for label in labels:
            label.setStyleSheet(common_css)
            label.setFont(font)

        comboBoxs = self.findChildren(QComboBox)
        for comboBox in comboBoxs:
            comboBox.setStyleSheet(common_css)
            comboBox.setFont(font)

        lineEdits = self.findChildren(QLineEdit)
        for lineEdit in lineEdits:
            lineEdit.setStyleSheet(common_css)
            lineEdit.setFont(font)

        textEdits = self.findChildren(QTextEdit)
        for textEdit in textEdits:
            textEdit.setStyleSheet(common_css)
            textEdit.setFont(font)
        

        self.show()

        # 将按钮点击事件与自定义的功能函数进行连接
        self.ui.pushButton_save.disconnect()
        self.ui.pushButton_factory.disconnect()
        self.ui.pushButton_run.disconnect()
        self.ui.pushButton_config_page.disconnect()
        self.ui.pushButton_run_page.disconnect()
        self.ui.pushButton_save.clicked.connect(self.on_pushButton_save_clicked)
        self.ui.pushButton_factory.clicked.connect(self.on_pushButton_factory_clicked)
        self.ui.pushButton_run.clicked.connect(self.on_pushButton_run_clicked)
        self.ui.pushButton_config_page.clicked.connect(self.on_pushButton_config_page_clicked)
        self.ui.pushButton_run_page.clicked.connect(self.on_pushButton_run_page_clicked)

        self.ui.comboBox_chat_type.disconnect()
        self.ui.comboBox_audio_synthesis_type.disconnect()
        self.ui.comboBox_chat_type.currentIndexChanged.connect(lambda index: self.oncomboBox_chat_type_IndexChanged(index))
        self.ui.comboBox_audio_synthesis_type.currentIndexChanged.connect(lambda index: self.oncomboBox_audio_synthesis_type_IndexChanged(index))

        self.ui.action_official_store.triggered.connect(self.openBrowser)

        # 创建节流函数，并将其保存为类的属性，delay秒内只执行一次
        self.throttled_save = self.throttle(self.save, 1)
        self.throttled_factory = self.throttle(self.factory, 1)
        self.throttled_run = self.throttle(self.run, 1)
        self.throttled_config_page = self.throttle(self.config_page, 0.5)
        self.throttled_run_page = self.throttle(self.run_page, 0.5)



    '''
        按钮相关的函数
    '''
    # 保存喵(开始堆shi喵)
    def save(self):
        global config, config_path
        try:
            with open(config_path, 'r', encoding="utf-8") as config_file:
                config_data = json.load(config_file)
        except Exception as e:
            logging.error(f"无法写入配置文件！\n{e}")
            self.show_message_box("错误", f"无法写入配置文件！\n{e}", QMessageBox.Critical)
            return False

        try:
            # 获取下拉框当前选中的内容
            platform = self.ui.comboBox_platform.currentText()
            if platform == "哔哩哔哩":
                config_data["platform"] = "bilibili"
            elif platform == "抖音":
                config_data["platform"] = "dy"
            elif platform == "快手":
                config_data["platform"] = "ks"

            # 获取单行文本输入框的内容
            room_display_id = self.ui.lineEdit_room_display_id.text()
            if False == self.is_alpha_numeric(room_display_id):
                logging.error("直播间号只由字母或数字组成，请勿输入错误内容")
                self.show_message_box("错误", "直播间号只由字母或数字组成，请勿输入错误内容", QMessageBox.Critical)
                return False
            config_data["room_display_id"] = room_display_id
                
            chat_type = self.ui.comboBox_chat_type.currentText()
            logging.info(chat_type)
            if chat_type == "复读机":
                config_data["chat_type"] = "none"
            elif chat_type == "ChatGPT":
                config_data["chat_type"] = "gpt"
            elif chat_type == "Claude":
                config_data["chat_type"] = "claude"
            elif chat_type == "ChatGLM":
                config_data["chat_type"] = "chatglm"
            elif chat_type == "Langchain_pdf":
                config_data["chat_type"] = "langchain_pdf"
            elif chat_type == "Langchain_pdf+gpt":
                config_data["chat_type"] = "langchain_pdf+gpt"
            elif chat_type == "Chatterbot":
                config_data["chat_type"] = "chatterbot"
            elif chat_type == "Langchain_pdf_local":
                config_data["chat_type"] = "langchain_pdf_local"

            need_lang = self.ui.comboBox_need_lang.currentText()
            if need_lang == "所有":
                config_data["need_lang"] = "none"
            elif need_lang == "中文":
                config_data["need_lang"] = "zh"
            elif need_lang == "英文":
                config_data["need_lang"] = "en"
            elif need_lang == "日文":
                config_data["need_lang"] = "jp"

            config_data["commit_log_type"] = self.ui.comboBox_commit_log_type.currentText()

            platform = self.ui.comboBox_platform.currentText()
            if platform == "哔哩哔哩":
                config_data["platform"] = "bilibili"
            elif platform == "抖音":
                config_data["platform"] = "dy"
            elif platform == "快手":
                config_data["platform"] = "ks"

            # 通用多行分隔符
            separators = [" ", "\n"]

            filter_before_must_str = self.ui.textEdit_filter_before_must_str.toPlainText()
            before_must_strs = [token.strip() for separator in separators for part in filter_before_must_str.split(separator) if (token := part.strip())]
            if 0 != len(before_must_strs):
                before_must_strs = before_must_strs[1:]
            config_data["filter"]["before_must_str"] = before_must_strs
            filter_after_must_str = self.ui.textEdit_filter_after_must_str.toPlainText()
            after_must_strs = [token.strip() for separator in separators for part in filter_after_must_str.split(separator) if (token := part.strip())]
            if 0 != len(after_must_strs):
                after_must_strs = after_must_strs[1:]
            config_data["filter"]["after_must_str"] = after_must_strs
            badwords_path = self.ui.lineEdit_filter_badwords_path.text()
            config_data["filter"]["badwords_path"] = badwords_path
            max_len = self.ui.lineEdit_filter_max_len.text()
            config_data["filter"]["max_len"] = int(max_len)
            max_char_len = self.ui.lineEdit_filter_max_char_len.text()
            config_data["filter"]["max_char_len"] = int(max_char_len)

            live2d_enable = self.ui.checkBox_live2d_enable.isChecked()
            config_data["live2d"]["enable"] = live2d_enable
            live2d_port = self.ui.lineEdit_live2d_port.text()
            config_data["live2d"]["port"] = int(live2d_port)

            openai_api = self.ui.lineEdit_openai_api.text()
            config_data["openai"]["api"] = openai_api
            # 获取多行文本输入框的内容
            openai_api_key = self.ui.textEdit_openai_api_key.toPlainText()
            api_keys = [token.strip() for separator in separators for part in openai_api_key.split(separator) if (token := part.strip())]
            if 0 != len(api_keys):
                api_keys = api_keys[1:]
            config_data["openai"]["api_key"] = api_keys

            chatgpt_model = self.ui.lineEdit_chatgpt_model.text()
            config_data["chatgpt"]["model"] = chatgpt_model
            chatgpt_temperature = self.ui.lineEdit_chatgpt_temperature.text()
            config_data["chatgpt"]["temperature"] = round(float(chatgpt_temperature), 1)
            chatgpt_max_tokens = self.ui.lineEdit_chatgpt_max_tokens.text()
            config_data["chatgpt"]["max_tokens"] = int(chatgpt_max_tokens)
            chatgpt_top_p = self.ui.lineEdit_chatgpt_top_p.text()
            config_data["chatgpt"]["top_p"] = round(float(chatgpt_top_p), 1)
            chatgpt_presence_penalty = self.ui.lineEdit_chatgpt_presence_penalty.text()
            config_data["chatgpt"]["presence_penalty"] = round(float(chatgpt_presence_penalty), 1)
            chatgpt_frequency_penalty = self.ui.lineEdit_chatgpt_frequency_penalty.text()
            config_data["chatgpt"]["frequency_penalty"] = round(float(chatgpt_frequency_penalty), 1)
            chatgpt_preset = self.ui.lineEdit_chatgpt_preset.text()
            config_data["chatgpt"]["preset"] = chatgpt_preset

            chatterbot_name = self.ui.lineEdit_chatterbot_name.text()
            config_data["chatterbot"]["name"] = chatterbot_name
            chatterbot_db_path = self.ui.lineEdit_chatterbot_db_path.text()
            config_data["chatterbot"]["db_path"] = chatterbot_db_path

            claude_slack_user_token = self.ui.lineEdit_claude_slack_user_token.text()
            config_data["claude"]["slack_user_token"] = claude_slack_user_token
            claude_bot_user_id = self.ui.lineEdit_claude_bot_user_id.text()
            config_data["claude"]["bot_user_id"] = claude_bot_user_id

            chatglm_api_ip_port = self.ui.lineEdit_chatglm_api_ip_port.text()
            config_data["chatglm"]["api_ip_port"] = chatglm_api_ip_port
            chatglm_max_length = self.ui.lineEdit_chatglm_max_length.text()
            config_data["chatglm"]["max_length"] = int(chatglm_max_length)
            chatglm_top_p = self.ui.lineEdit_chatglm_top_p.text()
            config_data["chatglm"]["top_p"] = round(float(chatglm_top_p), 1)
            chatglm_temperature = self.ui.lineEdit_chatglm_temperature.text()
            config_data["chatglm"]["temperature"] = round(float(chatglm_temperature), 2)

            langchain_pdf_openai_api_key = self.ui.lineEdit_langchain_pdf_openai_api_key.text()
            config_data["langchain_pdf"]["openai_api_key"] = langchain_pdf_openai_api_key
            langchain_pdf_data_path = self.ui.lineEdit_langchain_pdf_data_path.text()
            config_data["langchain_pdf"]["data_path"] = langchain_pdf_data_path
            langchain_pdf_separator = self.ui.lineEdit_langchain_pdf_separator.text()
            config_data["langchain_pdf"]["separator"] = langchain_pdf_separator
            langchain_pdf_chunk_size = self.ui.lineEdit_langchain_pdf_chunk_size.text()
            config_data["langchain_pdf"]["chunk_size"] = int(langchain_pdf_chunk_size)
            langchain_pdf_chunk_overlap = self.ui.lineEdit_langchain_pdf_chunk_overlap.text()
            config_data["langchain_pdf"]["chunk_overlap"] = int(langchain_pdf_chunk_overlap)
            langchain_pdf_model_name = self.ui.lineEdit_langchain_pdf_model_name.text()
            config_data["langchain_pdf"]["model_name"] = langchain_pdf_model_name
            langchain_pdf_chain_type = self.ui.lineEdit_langchain_pdf_chain_type.text()
            config_data["langchain_pdf"]["chain_type"] = langchain_pdf_chain_type
            # 获取复选框的选中状态
            langchain_pdf_show_cost = self.ui.checkBox_langchain_pdf_show_cost.isChecked()
            config_data["langchain_pdf"]["show_cost"] = langchain_pdf_show_cost

            langchain_pdf_local_slack_user_token = self.ui.lineEdit_langchain_pdf_local_slack_user_token.text()
            config_data["langchain_pdf_local"]["slack_user_token"] = langchain_pdf_local_slack_user_token
            langchain_pdf_local_bot_user_id = self.ui.lineEdit_langchain_pdf_local_bot_user_id.text()
            config_data["langchain_pdf_local"]["bot_user_id"] = langchain_pdf_local_bot_user_id
            langchain_pdf_local_data_path = self.ui.lineEdit_langchain_pdf_local_data_path.text()
            config_data["langchain_pdf_local"]["data_path"] = langchain_pdf_local_data_path
            langchain_pdf_local_separator = self.ui.lineEdit_langchain_pdf_local_separator.text()
            config_data["langchain_pdf_local"]["separator"] = langchain_pdf_local_separator
            langchain_pdf_local_chunk_size = self.ui.lineEdit_langchain_pdf_local_chunk_size.text()
            config_data["langchain_pdf_local"]["chunk_size"] = int(langchain_pdf_local_chunk_size)
            langchain_pdf_local_chunk_overlap = self.ui.lineEdit_langchain_pdf_local_chunk_overlap.text()
            config_data["langchain_pdf_local"]["chunk_overlap"] = int(langchain_pdf_local_chunk_overlap)
            langchain_pdf_local_embedding_model = self.ui.comboBox_langchain_pdf_local_embedding_model.currentText()
            config_data["langchain_pdf_local"]["embedding_model"] = langchain_pdf_local_embedding_model
            langchain_pdf_local_chain_type = self.ui.lineEdit_langchain_pdf_local_chain_type.text()
            config_data["langchain_pdf_local"]["chain_type"] = langchain_pdf_local_chain_type
            # 获取复选框的选中状态
            langchain_pdf_local_show_cost = self.ui.checkBox_langchain_pdf_local_show_cost.isChecked()
            config_data["langchain_pdf_local"]["show_cost"] = langchain_pdf_local_show_cost

            audio_synthesis_type = self.ui.comboBox_audio_synthesis_type.currentText()
            if audio_synthesis_type == "Edge-TTS":
                config_data["audio_synthesis_type"] = "edge-tts"
            elif audio_synthesis_type == "VITS-Fast":
                config_data["audio_synthesis_type"] = "vits"
            elif audio_synthesis_type == "elevenlabs":
                config_data["audio_synthesis_type"] = "elevenlabs"

            vits_config_path = self.ui.lineEdit_vits_config_path.text()
            config_data["vits"]["config_path"] = vits_config_path
            vits_api_ip_port = self.ui.lineEdit_vits_api_ip_port.text()
            config_data["vits"]["api_ip_port"] = vits_api_ip_port
            vits_character = self.ui.lineEdit_vits_character.text()
            config_data["vits"]["character"] = vits_character
            vits_speed = self.ui.lineEdit_vits_speed.text()
            config_data["vits"]["speed"] = float(vits_speed)

            edge_tts_voice = self.ui.comboBox_edge_tts_voice.currentText()
            config_data["edge-tts"]["voice"] = edge_tts_voice
            edge_tts_rate = self.ui.lineEdit_edge_tts_rate.text()
            config_data["edge-tts"]["rate"] = edge_tts_rate
            edge_tts_volume = self.ui.lineEdit_edge_tts_volume.text()
            config_data["edge-tts"]["volume"] = edge_tts_volume

            elevenlabs_api_key = self.ui.lineEdit_elevenlabs_api_key.text()
            config_data["elevenlabs"]["api_key"] = elevenlabs_api_key
            elevenlabs_voice = self.ui.lineEdit_elevenlabs_voice.text()
            config_data["elevenlabs"]["voice"] = elevenlabs_voice
            elevenlabs_model = self.ui.lineEdit_elevenlabs_model.text()
            config_data["elevenlabs"]["model"] = elevenlabs_model

            # SD
            sd_enable = self.ui.checkBox_sd_enable.isChecked()
            config_data["sd"]["enable"] = sd_enable
            sd_trigger = self.ui.lineEdit_sd_trigger.text()
            config_data["sd"]["trigger"] = sd_trigger
            sd_ip = self.ui.lineEdit_sd_ip.text()
            config_data["sd"]["ip"] = sd_ip
            sd_port = self.ui.lineEdit_sd_port.text()
            print(f"sd_port={sd_port}")
            config_data["sd"]["port"] = int(sd_port)
            sd_negative_prompt = self.ui.lineEdit_sd_negative_prompt.text()
            config_data["sd"]["negative_prompt"] = sd_negative_prompt
            sd_seed = self.ui.lineEdit_sd_seed.text()
            config_data["sd"]["seed"] = float(sd_seed)
            # 获取多行文本输入框的内容
            sd_styles = self.ui.textEdit_sd_styles.toPlainText()
            styles = [token.strip() for separator in separators for part in sd_styles.split(separator) if (token := part.strip())]
            if 0 != len(styles):
                styles = styles[1:]
            config_data["sd"]["styles"] = styles
            sd_cfg_scale = self.ui.lineEdit_sd_cfg_scale.text()
            config_data["sd"]["cfg_scale"] = int(sd_cfg_scale)
            sd_steps = self.ui.lineEdit_sd_steps.text()
            config_data["sd"]["steps"] = int(sd_steps)
            sd_hr_resize_x = self.ui.lineEdit_sd_hr_resize_x.text()
            config_data["sd"]["hr_resize_x"] = int(sd_hr_resize_x)
            sd_hr_resize_y = self.ui.lineEdit_sd_hr_resize_y.text()
            config_data["sd"]["hr_resize_y"] = int(sd_hr_resize_y)
            sd_enable_hr = self.ui.checkBox_sd_enable_hr.isChecked()
            config_data["sd"]["enable_hr"] = sd_enable_hr
            sd_hr_scale = self.ui.lineEdit_sd_hr_scale.text()
            config_data["sd"]["hr_scale"] = int(sd_hr_scale)
            sd_hr_second_pass_steps = self.ui.lineEdit_sd_hr_second_pass_steps.text()
            config_data["sd"]["hr_second_pass_steps"] = int(sd_hr_second_pass_steps)
            sd_denoising_strength = self.ui.lineEdit_sd_denoising_strength.text()
            config_data["sd"]["denoising_strength"] = float(sd_denoising_strength)

            header_useragent = self.ui.lineEdit_header_useragent.text()
            config_data["header"]["userAgent"] = header_useragent
            

            # logging.info(config_data)
        except Exception as e:
            logging.error(e)
            self.show_message_box("错误", f"配置项格式有误，请检查配置！\n{e}", QMessageBox.Critical)
            return False

        try:
            with open(config_path, 'w', encoding="utf-8") as config_file:
                json.dump(config_data, config_file, indent=2, ensure_ascii=False)
                config_file.flush()  # 刷新缓冲区，确保写入立即生效

            logging.info("配置数据已成功写入文件！程序将在3秒后重启~")
            self.show_message_box("提示", "配置数据已成功写入文件！程序将在3秒后重启~", QMessageBox.Information, 3000)

            self.restart_application()

            return True
        except Exception as e:
            logging.error(f"无法写入配置文件！\n{e}")
            self.show_message_box("错误", f"无法写入配置文件！\n{e}", QMessageBox.Critical)
            return False


    # 恢复出厂配置
    def factory(self):
        result = QMessageBox.question(
            None, "确认框", "您确定要恢复出厂配置吗？", QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.No:
            return

        source_file = 'config.json.bak'
        destination_file = 'config.json'

        try:
            with open(source_file, 'r', encoding="utf-8") as source:
                with open(destination_file, 'w', encoding="utf-8") as destination:
                    destination.write(source.read())
            logging.info("恢复出厂配置成功！")
        except Exception as e:
            logging.error(f"恢复出厂配置失败！\n{e}")
            self.show_message_box("错误", f"恢复出厂配置失败！\n{e}", QMessageBox.Critical)

        # 重载下配置
        self.init_config()


    # 运行
    def run(self):
        # if False == self.save():
        #     return

        # 暂停程序执行 3 秒钟
        # time.sleep(3)

        def delayed_run():
            # 切换到索引为 1 的页面
            self.ui.stackedWidget.setCurrentIndex(1)
            # 开冲！
            try:
                # self.run_external_command()
                # 连接信号与槽函数，用于接收输出并更新 UI
                # thread.output_ready.connect(self.ui.textBrowser.setText)

                # 连接 output_ready 信号和 update_textbrowser 槽函数
                # thread.output_ready.connect(self.update_textbrowser)

                # 创建线程对象
                self.my_thread = ExternalCommandThread()
                self.my_thread.platform = self.platform
                # 启动线程执行 run_external_command()
                self.my_thread.start()
                # 设置定时器间隔为 100 毫秒
                self.timer.setInterval(100)
                # 每次定时器触发时调用 update_text_browser 函数
                self.timer.timeout.connect(self.update_text_browser)
                # 启动定时器
                self.timer.start()

                self.show_message_box("提示", "开始运行喵~\n不要忘记保存配置~", QMessageBox.Information, 3000)
            except Exception as e:
                logging.error("平台配置出错，程序自爆~\n{e}")
                self.show_message_box("错误", f"平台配置出错，程序自爆~\n{e}", QMessageBox.Critical)
                exit(0)

        # 启动定时器，延迟  秒后触发函数执行
        QTimer.singleShot(100, delayed_run)


    # 切换至配置页面
    def config_page(self):
        self.ui.stackedWidget.setCurrentIndex(0)


    # 切换至运行页面
    def run_page(self):
        self.ui.stackedWidget.setCurrentIndex(1)


    # 保存配置
    def on_pushButton_save_clicked(self):
        self.throttled_save()

    # 初始化配置
    def on_pushButton_factory_clicked(self):
        self.throttled_factory()

    # 运行
    def on_pushButton_run_clicked(self):
        self.throttled_run()


    # 切换至配置页面
    def on_pushButton_config_page_clicked(self):
        self.throttled_config_page()

    
    # 切换至运行页面
    def on_pushButton_run_page_clicked(self):
        self.throttled_run_page()



    '''
        餐单栏相关的函数
    '''
    def openBrowser(self):
        url = QUrl("https://github.com/Ikaros-521/AI-Vtuber")  # 指定要打开的网页地址
        QDesktopServices.openUrl(url)


    '''
        UI操作的函数
    '''
    # 聊天类型改变 加载显隐不同groupBox
    def oncomboBox_chat_type_IndexChanged(self, index):
        # 各index对应的groupbox的显隐值
        visibility_map = {
            0: (0, 0, 0, 0, 0, 0, 0, 0),
            1: (1, 1, 0, 0, 0, 0, 1, 0),
            2: (0, 0, 1, 0, 0, 0, 0, 0),
            3: (0, 0, 0, 1, 0, 0, 0, 0),
            4: (0, 0, 0, 0, 1, 0, 0, 0),
            5: (0, 0, 0, 0, 1, 0, 0, 0),
            6: (0, 0, 0, 0, 0, 1, 0, 0),
            7: (0, 0, 0, 0, 0, 0, 0, 1)
        }

        visibility_values = visibility_map.get(index, (0, 0, 0, 0, 0, 0, 0, 0))

        self.ui.groupBox_openai.setVisible(visibility_values[0])
        self.ui.groupBox_chatgpt.setVisible(visibility_values[1])
        self.ui.groupBox_claude.setVisible(visibility_values[2])
        self.ui.groupBox_chatglm.setVisible(visibility_values[3])
        self.ui.groupBox_langchain_pdf.setVisible(visibility_values[4])
        self.ui.groupBox_chatterbot.setVisible(visibility_values[5])
        self.ui.groupBox_header.setVisible(visibility_values[6])
        self.ui.groupBox_langchain_pdf_local.setVisible(visibility_values[7])

    
    # 语音合成类型改变 加载显隐不同groupBox
    def oncomboBox_audio_synthesis_type_IndexChanged(self, index):
        # 各index对应的groupbox的显隐值
        visibility_map = {
            0: (1, 0, 0),
            1: (0, 1, 0),
            2: (0, 0, 1)
        }

        visibility_values = visibility_map.get(index, (0, 0, 0))

        self.ui.groupBox_edge_tts.setVisible(visibility_values[0])
        self.ui.groupBox_vits_fast.setVisible(visibility_values[1])
        self.ui.groupBox_elevenlabs.setVisible(visibility_values[2])


    # 输出文本到运行页的textbrowser
    # def output_to_textbrowser(self, content):
    #     max_content_len = 10000

    #     text = self.ui.textBrowser.toPlainText() + content  # 将新内容添加到已有内容后面
    #     if len(text) > max_content_len:
    #         text = text[-max_content_len:]  # 保留最后一万个字符，截断超出部分
    #     self.ui.textBrowser.setText(text)

    
    # def update_textbrowser(self, output_text):
    #     cursor = self.ui.textBrowser.textCursor()
    #     cursor.movePosition(QTextCursor.End)
    #     cursor.insertText(output_text)
    #     self.ui.textBrowser.setTextCursor(cursor)
    #     self.ui.textBrowser.ensureCursorVisible()

    
    # 获取一个文件最后num_lines行数据
    def load_last_lines(self, file_path, num_lines=1000):
        lines = []
        with open(file_path, 'r', encoding="utf-8") as file:
            # 将文件内容逐行读取到列表中
            lines = file.readlines()

        # 只保留最后1000行文本
        last_lines = lines[-num_lines:]

        # 倒序排列文本行
        last_lines.reverse()

        return last_lines


    # 清空text_browser，显示文件内的数据
    def update_text_browser(self):
        global file_path

        # 记录当前的滚动位置
        scroll_position = self.ui.textBrowser.verticalScrollBar().value()

        # 加载文件的最后1000行文本
        last_lines = self.load_last_lines(file_path)

        # 获取当前文本光标
        cursor = self.ui.textBrowser.textCursor()

        # 获取当前选中的文本
        selected_text = cursor.selectedText()

        # 判断是否有选中的文本
        has_selection = len(selected_text) > 0

        # 清空 textBrowser
        self.ui.textBrowser.clear()

        # 设置文本浏览器打开外部链接功能
        self.ui.textBrowser.setOpenExternalLinks(True)

        # 将文本逐行添加到 textBrowser 中
        for line in last_lines:
            self.ui.textBrowser.insertPlainText(line)

        # 恢复滚动位置
        if not has_selection:
            self.ui.textBrowser.verticalScrollBar().setValue(scroll_position)


    '''
        通用的函数
    '''
    def restart_application(self):
        QApplication.exit()  # Exit the current application instance
        python = sys.executable
        os.execl(python, python, *sys.argv)  # Start a new instance of the application


    # 字符串是否只由字母或数字组成
    def is_alpha_numeric(self, string):
        pattern = r'^[a-zA-Z0-9]+$'
        return re.match(pattern, string) is not None


    # 显示提示弹窗框,自动关闭时间（单位：毫秒）
    def show_message_box(self, title, text, icon=QMessageBox.Information, timeout_ms=60 * 1000):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)

        def close_message_box():
            msg_box.close()

        QTimer.singleShot(timeout_ms, close_message_box)

        msg_box.exec_()


    # 套娃运行喵（会卡死）
    def run_external_command(self):
        module = importlib.import_module(self.platform)
        process = subprocess.Popen([sys.executable, '-c', 'import {}'.format(module.__name__)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        output_text = output.decode("utf-8")  # 将字节流解码为字符串
        self.output_to_textbrowser(output_text)

        # 调用 start_server() 并将输出追加到 textbrowser
        start_server_output = module.start_server()  # 调用 start_server() 函数并获取输出
        output_text += start_server_output
        

    # 节流函数，单位时间内只执行一次函数
    def throttle(self, func, delay):
        last_executed = 0

        def throttled(*args, **kwargs):
            nonlocal last_executed
            current_time = time.time()
            if current_time - last_executed > delay:
                last_executed = current_time
                func(*args, **kwargs)

        return throttled   
    

# 执行额外命令的线程
class ExternalCommandThread(QThread):
    output_ready = pyqtSignal(str)

    def __init__(self, platform=None):
        super().__init__()
        self.platform = platform

    def run(self):
        if self.platform is None:
            # 处理没有传递 platform 的情况
            self.output_ready.emit("没有传入platform，取名为寄！")
            return
        
        logging.debug(f"platform={self.platform}")

        module = importlib.import_module(self.platform)
        process = subprocess.Popen([sys.executable, '-c', 'import {}'.format(module.__name__)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        # logging.debug(output)
        # output_text = output.decode("utf-8")  # 将字节流解码为字符串

        # 调用 start_server() 并将输出追加到 textbrowser
        start_server_output = module.start_server()  # 调用 start_server() 函数并获取输出
        # output_text += start_server_output


# web服务线程
class WebServerThread(QThread):
    def run(self):
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", web_server_port), Handler) as httpd:
            logging.info(f"Web运行在端口：{web_server_port}")
            logging.info(f"可以直接访问Live2D页， http://127.0.0.1:{web_server_port}/Live2D/")
            httpd.serve_forever()



# 程序入口
if __name__ == '__main__':
    common = Common()

    if getattr(sys, 'frozen', False):
        # 当前是打包后的可执行文件
        bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(sys.executable)))
        file_relative_path = os.path.dirname(os.path.abspath(bundle_dir))
    else:
        # 当前是源代码
        file_relative_path = os.path.dirname(os.path.abspath(__file__))

    # logging.info(file_relative_path)

    # 创建日志文件夹
    log_dir = os.path.join(file_relative_path, 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建音频输出文件夹
    audio_out_dir = os.path.join(file_relative_path, 'out')
    if not os.path.exists(audio_out_dir):
        os.makedirs(audio_out_dir)
        
    # # 创建配置文件夹
    # config_dir = os.path.join(file_relative_path, 'config')
    # if not os.path.exists(config_dir):
    #     os.makedirs(config_dir)

    # 配置文件路径
    config_path = os.path.join(file_relative_path, 'config.json')

    # 日志文件路径
    file_path = "./log/log-" + common.get_bj_time(1) + ".txt"
    Configure_logger(file_path)

    # 获取 httpx 库的日志记录器
    httpx_logger = logging.getLogger("httpx")
    # 设置 httpx 日志记录器的级别为 WARNING
    httpx_logger.setLevel(logging.WARNING)

    web_server_port = 12345

    # 本地测试时候的日志设置
    '''
    # 日志格式
    log_format = '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    # 日志文件路径
    file_path = os.path.join(file_relative_path, 'log/log.txt')

    # 自定义控制台输出类
    class ColoredStreamHandler(logging.StreamHandler):
        """
        自定义 StreamHandler 类，用于在控制台中为不同级别的日志信息设置不同的颜色
        """
        def __init__(self):
            super().__init__()
            self._colors = {
                logging.DEBUG: '\033[1;34m',    # 蓝色
                logging.INFO: '\033[1;37m',     # 白色
                logging.WARNING: '\033[1;33m',  # 黄色
                logging.ERROR: '\033[1;31m',    # 红色
                logging.CRITICAL: '\033[1;35m'  # 紫色
            }

        def emit(self, record):
            # 根据日志级别设置颜色
            color = self._colors.get(record.levelno, '\033[0m')  # 默认为关闭颜色设置
            # 设置日志输出格式和颜色
            self.stream.write(color)
            super().emit(record)
            self.stream.write('\033[0m')

    # 创建 logger 对象并设置日志级别
    logger = logging.getLogger(__name__)
    logging.setLevel(logging.DEBUG)

    # 创建 FileHandler 对象和 StreamHandler 对象并设置日志级别
    fh = logging.FileHandler(file_path, encoding='utf-8', mode='a+')
    fh.setLevel(logging.DEBUG)
    ch = ColoredStreamHandler()
    ch.setLevel(logging.DEBUG)

    # 创建 Formatter 对象并设置日志输出格式
    formatter = logging.Formatter(log_format)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # 将 FileHandler 对象和 ColoredStreamHandler 对象添加到 logger 对象中
    logging.addHandler(fh)
    logging.addHandler(ch)
    '''


    logging.debug("配置文件路径=" + str(config_path))

    # 实例化配置类
    config = Config(config_path)

    try:
        if config.get("live2d", "enable"):
            web_server_port = int(config.get("live2d", "port"))
            # 创建 web服务线程
            web_server_thread = WebServerThread()
            # 运行 web服务线程
            web_server_thread.start()
    except Exception as e:
        logging.error(e)
        exit(0)

    e = AI_VTB()

    sys.exit(e.app.exec())