# AI Vtuber

抖音版，一个由gpt/claude驱动的虚拟主播，可以在抖音直播中与观众实时互动。它使用自然语言处理和文本转语音技术生成对观众问题的回答。（edge-tts/VITS）

## 运行环境

- Python 3.10+

## dy.py (ChatGPT/claude + Edge-TTS/VITS-Fast)
在命令行中使用以下命令安装所需库：
```bash
pip install -r requirements.txt
```

配置都在`config.json`  
```
{
  // https://live.douyin.com/123，例如:123
  "room_display_id": "你的直播间号",
  // 选用的聊天类型：gpt/claude/none 其中none就是复读机模式
  "chat_type": "none",
  // 弹幕语言筛选，none就是全部语言，en英文，jp日文，zh中文
  "need_lang": "none",
  // 请求gpt/claude时，携带的字符串头部，用于给每个对话追加固定限制
  "before_promet": "请简要回复:",
  // 请求gpt/claude时，携带的字符串尾部
  "after_promet": "",
  // 本地违禁词数据路径（你如果不需要，可以清空文件内容）
  "badwords_path": "data/badwords.txt",
  // 最长阅读的英文单词数（空格分隔）
  "max_len": 30,
  // 最长阅读的字符数，双重过滤，避免溢出
  "max_char_len": 50,
  "openai": {
    "api": "https://api.openai.com/v1",
    "api_key": [
      "你的api key"
    ]
  },
  // claude相关配置
  "claude": {
    // claude相关配置
    // 参考：https://github.com/bincooo/claude-api#readme
    "slack_user_token": "",
    "bot_user_id": ""
  },
  // 语音合成类型选择 edge-tts/vits
  "audio_synthesis_type": "edge-tts",
  // vits相关配置
  "vits": {
    "vits_config_path": "E:\\GitHub_pro\\VITS-fast-fine-tuning\\inference\\finetune_speaker.json",
    "vits_api_ip_port": "http://127.0.0.1:7860",
    "character": "ikaros"
  },
  // edge-tts选定的说话人
  "tts_voice": "zh-CN-XiaoyiNeural",
  // chatterbot相关配置（留了配置，但是注释了功能，感觉没人用）
  "chatterbot": {
    // 机器人名
    "name": "bot",
    // bot数据库路径
    "db_path": "db.sqlite3"
  },
  // chatgpt相关配置
  "chatgpt": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.9,
    "max_tokens": 2048,
    "top_p": 1,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "preset": "请扮演一个AI虚拟主播。不要回答任何敏感问题！不要强调你是主播，只需要回答问题！"
  },
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"
}
```

运行`python dy.py`  


### 许可证
MIT许可证。详情请参阅LICENSE文件。

## 扩展

### ChatterBot
ChatterBot 是一个开源的 Python 聊天机器人框架，使用机器学习算法（尤其是自然语言处理、文本语义分析等）来实现基于规则和语境的自动聊天系统。它可以让开发者通过简单的配置和训练，构建出各种类型的聊天机器人，包括问答机器人、任务型机器人、闲聊机器人等。

ChatterBot 的核心思想是：基于历史对话数据，使用机器学习和自然语言处理技术来分析和预测用户输入，然后生成响应。基于这种方法，聊天机器人的反应会更加智能、灵活、接近人类对话的方式。此外，ChatterBot 支持多种存储方式，如 JSON、SQLAlchemy、MongoDB 等，以及多种接口调用方式，如 RESTful API、WebSocket 等，方便开发者在不同场景中进行集成。

总的来说，ChatterBot 是一个非常强大、灵活、易用的聊天机器人框架，帮助开发者快速搭建出个性化、定制化的聊天机器人，从而提升用户体验和服务质量。

## 致谢
弹幕等信息数据爬取 - [douyin-live](https://github.com/YunzhiYike/douyin-live)  
