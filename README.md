# AI Vtuber

<div style="text-align: center;">
_✨ AI Vtuber ✨_

<a href="https://github.com/Ikaros-521/AI-Vtuber/stargazers">
    <img alt="GitHub stars" src="https://img.shields.io/github/stars/Ikaros-521/AI-Vtuber?color=%09%2300BFFF&style=flat-square">
</a>
<a href="https://github.com/Ikaros-521/AI-Vtuber/issues">
    <img alt="GitHub issues" src="https://img.shields.io/github/issues/Ikaros-521/AI-Vtuber?color=Emerald%20green&style=flat-square">
</a>
<a href="https://github.com/Ikaros-521/AI-Vtuber/network">
    <img alt="GitHub forks" src="https://img.shields.io/github/forks/Ikaros-521/AI-Vtuber?color=%2300BFFF&style=flat-square">
</a>
<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/Ikaros-521/AI-Vtuber.svg" alt="license">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
</a>

</div>

AI Vtuber是一个由`ChatterBot/GPT/Claude/langchain_pdf+gpt/chatglm/langchain_pdf_local`驱动的虚拟主播（Live2D），可以在`Bilibili/抖音/快手`直播中与观众实时互动。它使用自然语言处理和文本转语音技术(`Edge-TTS/VITS-Fast/elevenlabs`)生成对观众问题的回答。


## 📖项目结构

- `config.json`，配置文件。
- `main.py`，GUI主程序。会根据配置调用各平台程序
- `utils`文件夹，存储聊天、音频、通用类相关功能的封装实现
- `data`文件夹，存储数据文件和违禁词
- `log`文件夹，存储运行日志
- `out`文件夹，存储edge-tts输出的音频文件
- `Live2D`文件夹，存储Live2D源码及模型


## 下载项目

首先你得装个`git`（啥，没装？百度），当然也可以直接在页面切换分支后下载各版本ZIP压缩包。    
```
# 主线
git clone https://github.com/Ikaros-521/AI-Vtuber.git

# owner分支
git clone -b owner https://github.com/Ikaros-521/AI-Vtuber.git

# dev分支
git clone -b dev https://github.com/Ikaros-521/AI-Vtuber.git
```


## 💿运行环境

python：3.10.11  
各个版本的依赖的库在 requirements_xx.txt 中，请自行安装。  

依赖版本参考`requirements_common.txt`  

安装命令参考（注意文件命名，对应各个版本）：  
```
pip install -r requirements_bilibili.txt
pip install -r requirements_dy.txt
pip install -r requirements_ks.txt
```

## 🔧配置

配置都在`config.json`  
```
{
  // 你的直播间号,兼容全平台，都是直播间页面的链接中最后的数字和字母。例如:123
  "room_display_id": "你的直播间号",
  // 选用的聊天类型：chatterbot/gpt/claude/langchain_pdf/langchain_pdf+gpt/chatglm/langchain_pdf_local/none 其中none就是复读机模式
  "chat_type": "none",
  // 弹幕语言筛选，none就是全部语言，en英文，jp日文，zh中文
  "need_lang": "none",
  // 请求gpt/claude时，携带的字符串头部，用于给每个对话追加固定限制
  "before_prompt": "请简要回复:",
  // 请求gpt/claude时，携带的字符串尾部
  "after_prompt": "",
  // 弹幕日志类型，用于记录弹幕触发时记录的内容，默认只记录回答，降低当用户使用弹幕日志显示在直播间时，因为用户的不良弹幕造成直播间被封禁问题
  "commit_log_type": "回答",
  "filter": {
    // 弹幕过滤，必须携带的触发前缀字符串（任一）
    "before_must_str": [],
    // 弹幕过滤，必须携带的触发后缀字符串（任一）
    "after_must_str": [
      ".",
      "。",
      "?",
      "？"
    ],
    // 本地违禁词数据路径（你如果不需要，可以清空文件内容）
    "badwords_path": "data/badwords.txt",
    // 最长阅读的英文单词数（空格分隔）
    "max_len": 30,
    // 最长阅读的字符数，双重过滤，避免溢出
    "max_char_len": 50
  },
  // Live2D皮
  "live2d": {
    // 是否启用
    "enable": true,
    // web服务监听端口
    "port": 12345
  },
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
  // chatglm相关配置
  "chatglm": {
    "api_ip_port": "http://127.0.0.1:8000",
    "max_length": 2048,
    "top_p": 0.7,
    "temperature": 0.95
  },
  // langchain_pdf 和 langchain_pdf+gpt 相关配置
  "langchain_pdf": {
    // 你的openai api key
    "openai_api_key": "你的api key",
    // 加载的本地pdf数据文件路径（到x.pdf）,如：./data/伊卡洛斯百度百科.pdf
    "data_path": "",
    // 拆分文本的分隔符
    "separator": "\n",
    // 每个文本块的最大字符数(文本块字符越多，消耗token越多，回复越详细)
    "chunk_size": 100,
    // 两个相邻文本块之间的重叠字符数。这种重叠可以帮助保持文本的连贯性，特别是当文本被用于训练语言模型或其他需要上下文信息的机器学习模型时
    "chunk_overlap": 50,
    // 选择的openai的模型
    "model_name": "gpt-3.5-turbo-0301",
    // 文档结合链的类型
    "chain_type": "stuff",
    // 显示openai token的消耗
    "show_cost": true
  },
  "langchain_pdf_local": {
    // claude相关配置
    // 参考：https://github.com/bincooo/claude-api#readme
    "bot_user_id": "",
    "slack_user_token": "",
    // 选择输入的pdf数据
    "data_path": "data/伊卡洛斯百度百科.zip",
    "separator": "\n",
    "chunk_size": 100,
    "chunk_overlap": 50,
    // 默认模型
    "embedding_model": "sebastian-hofstaetter/distilbert-dot-tas_b-b256-msmarco",
    // 最大查询数据库次数。限制次数有助于节省token
    "max_query": 3,
    "question_prompt": "请根据以上content信息进行归纳总结，并结合question的内容给出一个符合content和question语气、语调、背景的回答。不要出现'概括''综上''感谢'等字样，向朋友直接互相交流即可。如果发现不能content的信息与question不相符，抛弃content的提示，直接回答question即可。任何情况下都要简要地回答!",
    "chain_type": "stuff",
    "show_cost": true
  },
  // 语音合成类型选择 edge-tts/vits/elevenlabs
  "audio_synthesis_type": "edge-tts",
  // vits相关配置
  "vits": {
    // 配置文件的路径
    "vits_config_path": "E:\\GitHub_pro\\VITS-fast-fine-tuning\\inference\\finetune_speaker.json",
    // 推理服务运行的链接（需要完整的URL）
    "vits_api_ip_port": "http://127.0.0.1:7860",
    // 选择的说话人，配置文件中的speaker中的其中一个
    "character": "ikaros"
  },
  // edge-tts相关配置
  "edge-tts": {
    // edge-tts选定的说话人(cmd执行：edge-tts -l 可以查看所有支持的说话人)
    "voice": "zh-CN-XiaoyiNeural"
    // 语速增益 默认是 +0%，可以增减，注意 + - %符合别搞没了，不然会影响语音合成
    "rate": "+0%",
    // 音量增益 默认是 +0%，可以增减，注意 + - %符合别搞没了，不然会影响语音合成
    "volume": "+0%"
  },
  // elevenlabs相关配置
  "elevenlabs": {
    // elevenlabs密钥，可以不填，默认也有一定额度的免费使用权限，具体多少不知道
    "api_key": "",
    // 选择的说话人名
    "voice": "Domi",
    // 选择的模型
    "model": "eleven_monolingual_v1"
  },
  // chatterbot相关配置
  "chatterbot": {
    // 机器人名
    "name": "bot",
    // bot数据库路径
    "db_path": "db.sqlite3"
  },
  // chatgpt相关配置
  "chatgpt": {
    "model": "gpt-3.5-turbo",
    // 控制生成文本的随机性。较高的温度值会使生成的文本更随机和多样化，而较低的温度值会使生成的文本更加确定和一致。
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

### chatgpt代理
例如：[API2D](https://api2d.com/wiki/doc)  
```
"openai": {
  // 代理地址，需要和官方接口一致的才行。例如：api2d
  "api": "https://oa.api2d.net/v1",
  // 代理站提供的密钥
  "api_key": [
    "fkxxxxxxxxxxx"
  ]
}
```

或者纯代理的镜像站：  
- https://openai-pag.wangzhishi.net/


## 🎉使用

各版本都需要做的前期准备操作。  
`chatterbot`相关安装参考[chatterbot/README.md](chatterbot/README.md)  

修改`config.json`的配置，配好哈，注意JSON数据格式  

弹幕自带过滤，且需要弹幕以。或.或？结尾才能触发，请注意。  

### 哔哩哔哩版

在命令行中使用以下命令安装所需库：
```
pip install -r requirements_bilibili.txt
```

运行 `python main.py`  

### 抖音版

在命令行中使用以下命令安装所需库：
```
pip install -r requirements_dy.txt
```

先安装第三方弹幕捕获软件，参考[补充-抖音](#dy)

运行 `python main.py`  

### 抖音版_旧版（不稳定）

在命令行中使用以下命令安装所需库：
```
pip install -r requirements_dy.txt
```

运行前请重新生成一下protobuf文件，因为机器系统不一样同时protobuf版本也不一样所以不能拿来直接用～  
```
protoc -I . --python_out=. dy.proto
```
ps:依赖[golang](https://go.dev/dl/)环境，还没有的话，手动补一补[protobuf](https://github.com/protocolbuffers/protobuf/releases)  

运行 `python main.py`  

### 快手版

在命令行中使用以下命令安装所需库：
```
pip install -r requirements_ks.txt
```

运行前请重新生成一下protobuf文件，因为机器系统不一样同时protobuf版本也不一样所以不能拿来直接用～  
```
protoc -I . --python_out=. ks.proto
```
ps:依赖[golang](https://go.dev/dl/)环境，还没有的话，手动补一补[protobuf](https://github.com/protocolbuffers/protobuf/releases)  

运行 `python main.py`  

## 开发
### UI设计
打开QT设计师~o( =∩ω∩= )m `pyqt5-tools designer`  
生成UI代码 `pyuic5 -o UI_main.py ui\main.ui`  
对UI做改动时，加入新的配置，一般需要修改init_config和save部分，新配置的读取和写入部分。  


## 打包懒人包(错误案例)

1、本地装有conda环境  
2、在本文件夹创建虚拟环境  
`conda create --prefix ./venv python=3.10`  
3、安装依赖  
`venv\python.exe -m pip install -r requirements_bilibili.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`  
`venv\python.exe -m pip install -r requirements_dy.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`  
`venv\python.exe -m pip install -r requirements_ks.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`  
4、安装chatterbot（可选）
`venv\python.exe -m pip install spacy SQLAlchemy==1.3.24 -i https://pypi.tuna.tsinghua.edu.cn/simple`  
前提是你在当前目录下有clone chatterbot的项目（自行调整路径关系）  
`venv\python.exe setup.py install`  
5、修改`audio.py`中`edge-tts`的调用实现  


## FAQ 常问问题

### 部署过程问题

#### 1.CondaSSLError: OpenSSL appears to be unavailable on this machine
本地已经有`Anaconda`环境，在执行 半自动包的`1.创建虚拟环境.bat`时，出现报错`CondaSSLError: OpenSSL appears to be unavailable on this machine `
![image](https://github.com/Ikaros-521/AI-Vtuber/assets/40910637/8f6af198-a362-40ad-9c33-5f9576cdcfa8)

解决方案：参考[https://blog.csdn.net/mynameisyaxuan/article/details/128323026](https://blog.csdn.net/mynameisyaxuan/article/details/128323026)  

#### 2.ModuleNotFoundError: No module named 'xxx' 大同小异
都是依赖库缺失问题，可以打开`requirements_bilibili.txt`/`requirements_dy.txt`/`requirements_ks.txt`内查看需要安装的依赖（可能还是遗漏...）  
视情况更换镜像源，国内推荐清华源，如果清华源没有缺失的库，可以走pypi的源，安装命令如：`pip install PyQt5 -i https://pypi.tuna.tsinghua.edu.cn/simple`  
注意：请在虚拟环境中安装！！！（如果你是根据半自动整合包做的话，先激活虚拟环境`conda activate ai_vtb`，然后进行安装）  
```
https://pypi.org/simple
https://pypi.python.org/simple/
https://pypi.tuna.tsinghua.edu.cn/simple
```

##### ModuleNotFoundError: No module named 'PyQt5'
半自动包 运行`3.GUI运行.bat`时，出现  
```
Traceback (most recent call last):
  File "F:\github_pro\AI-Vtuber\main.py", line 10, in <module>
    from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QComboBox, QLineEdit, QTextEdit, QDialog
ModuleNotFoundError: No module named 'PyQt5'
```

解决方案：手动补装`PyQt5`，需要注意，得在`ai_vtb`的虚拟环境中安装  
可以发现最左侧有这个括号，表示你激活了`ai_vtb`的虚拟环境中，然后你在运行 后面的pip安装 `(ai_vtb) F:\github_pro\AI-Vtuber>pip install PyQt5`
![MD_DDZ4{SX 5WPHB(B9M7JA](https://github.com/Ikaros-521/AI-Vtuber/assets/40910637/ee3ad055-b562-4f12-8797-d6aff44331be)

##### ModuleNotFoundError: No module named 'langid'
半自动包 运行`3.GUI运行.bat`时，出现  
```
Traceback (most recent call last):
  File "F:\github_pro\AI-Vtuber\main.py", line 20, in <module>
    from utils.common import Common
  File "F:\github_pro\AI-Vtuber\utils\common.py", line 8, in <module>
    import langid
ModuleNotFoundError: No module named 'langid'
```

解决方案：手动补装`langid`，需要注意，得在`ai_vtb`的虚拟环境中安装， `pip install langid`  
![image](https://github.com/Ikaros-521/AI-Vtuber/assets/40910637/3047406b-a25c-4e53-9248-a21684dbaea4)
如果遇到上图安装失败的问题 ， 走官方源下载 `pip install langid -i https://pypi.python.org/simple/`
![HVD873 MJYU3U5HR8V ~PY4](https://github.com/Ikaros-521/AI-Vtuber/assets/40910637/0f08c00f-f7ac-41dd-a6a4-7f7539efa843)


##### ModuleNotFoundError: No module named 'profanity'
半自动包 运行`3.GUI运行.bat`时，出现  
```
Traceback (most recent call last):
  File "F:\github_pro\AI-Vtuber\main.py", line 20, in <module>
    from utils.common import Common
  File "F:\github_pro\AI-Vtuber\utils\common.py", line 10, in <module>
    from profanity import profanity
ModuleNotFoundError: No module named 'profanity'
```

解决方案：手动补装`profanity`，需要注意，得在`ai_vtb`的虚拟环境中安装， `pip install profanity`  
![I{UGQKZR029GFMQD{}K{82R](https://github.com/Ikaros-521/AI-Vtuber/assets/40910637/3501aaca-9a08-45e3-b7bd-6aa60f9ea4b9)

##### ModuleNotFoundError: No module named 'ahocorasick'
半自动包 运行`3.GUI运行.bat`时，出现  
```
Traceback (most recent call last):
  File "F:\github_pro\AI-Vtuber\main.py", line 20, in <module>
    from utils.common import Common
  File "F:\github_pro\AI-Vtuber\utils\common.py", line 11, in <module>
    import ahocorasick
ModuleNotFoundError: No module named 'ahocorasick'
```

解决方案：手动补装`pyahocorasick`，需要注意，得在`ai_vtb`的虚拟环境中安装， `pip install pyahocorasick`  
![9WYG0P%K6 ZMERSE8K9TI5R](https://github.com/Ikaros-521/AI-Vtuber/assets/40910637/b58927ac-c9f3-4e25-8b78-ccec09543735)


### 使用过程问题

#### 1.openai 接口报错:《empty message》
可能是API KEY过期了/额度没了，请检查API KEY是否可用。  
在线测试参考：  
[chatgpt-html](http://ikaros521.eu.org/chatgpt-html/)  
[ChatGPT-Next-Web](https://chat-gpt-next-web-ikaros-521.vercel.app/)  




## 补充

### <span id="dy">抖音弹幕获取</span>
`dy.py`稳定：[dy-barrage-grab](https://gitee.com/haodong108/dy-barrage-grab)  
请到此仓库的releases下载官方软件包，并仔细阅读官方的使用说明，运行后能在cmd看到弹幕消息的话，即为成功。  


`dy_old.py`不稳定：[douyin-live](https://github.com/YunzhiYike/douyin-live)   

### 快手弹幕获取
[kuaishou-live](https://github.com/YunzhiYike/kuaishou-live)  

### Claude
[claude-api](https://github.com/bincooo/claude-api)  

### ChatGLM
[ChatGLM-6B](https://github.com/THUDM/ChatGLM-6B)  

### langchain_pdf
参考：[LangChainSummarize](https://github.com/Ikaros-521/LangChainSummarize)

### elevenlabs
[elevenlabs官网](https://beta.elevenlabs.io/)  
[官方文档](https://docs.elevenlabs.io/api-reference/quick-start/introduction)  
不注册账号也可以使用，不过应该是有限制的（具体多少未知）。免费账号拥有每月1万字的额度。  

### ChatterBot
[官方仓库](https://github.com/gunthercox/ChatterBot)  
ChatterBot 是一个开源的 Python 聊天机器人框架，使用机器学习算法（尤其是自然语言处理、文本语义分析等）来实现基于规则和语境的自动聊天系统。它可以让开发者通过简单的配置和训练，构建出各种类型的聊天机器人，包括问答机器人、任务型机器人、闲聊机器人等。

ChatterBot 的核心思想是：基于历史对话数据，使用机器学习和自然语言处理技术来分析和预测用户输入，然后生成响应。基于这种方法，聊天机器人的反应会更加智能、灵活、接近人类对话的方式。此外，ChatterBot 支持多种存储方式，如 JSON、SQLAlchemy、MongoDB 等，以及多种接口调用方式，如 RESTful API、WebSocket 等，方便开发者在不同场景中进行集成。

总的来说，ChatterBot 是一个非常强大、灵活、易用的聊天机器人框架，帮助开发者快速搭建出个性化、定制化的聊天机器人，从而提升用户体验和服务质量。  

### Live2D
源自：[CyberWaifu](https://github.com/jieran233/CyberWaifu)  

### langchain_pdf_local 向量数据库解析
如果本地电脑的配置太低，可以使用 [faiss_text2vec.ipynb](https://drive.google.com/file/d/1rbt2Yv7_pC1cmuODwmR2-1_cxFBFOfn8/view?usp=sharing) 云端解析向量数据库，拷贝回本地后再使用即可
- author: [HildaM/text2vec_colab](https://github.com/HildaM/text2vec_colab)

## 待办事项
- 懒人包的制作
- 快手平台的重新兼容
- live2d的嘴型匹配

## 📝 更新日志

<details>
<summary>展开/收起</summary>

### 2023-06-13
兼容本地版ChatGLM API接口  

### 2023-06-16
增加Edge-TTS的语速、音量调节参数。  

### 2023-06-17
- 增加GUI版。
- 增加GUI运行的bat文件，需要配合本地虚拟环境运行。请到releases下载。
- 对config.json的结构做了调整，增加了弹幕前后缀过滤配置。
- 增加langchain_pdf_local的配置内容，待和主线整合后合并。

### 2023-06-18
- 修复部分GUI的bug
- 整合到主线
- 新增本地live2d模型加载

### 2023-06-20
- 补充了整合包的打包方式
- 音频合成更改多线程为队列结构，解决高并发的崩溃问题
- langchain_pdf_local 增加 [GanymedeNil/text2vec-large-chinese](https://huggingface.co/GanymedeNil/text2vec-large-chinese) 模型，该模型在中文解析上很好
- 增加弹幕触发,回复部分日志记录时，每20字符自动换行的机制
- 修改edge-tts合成音频的文件名范围
- 更换抖音方案为`dy-barrage-grab`  
- GUI新增 弹幕日志类型、修改langchain_pdf_local的模型下拉选择

### 2023-06-21
- 修复语音合成内容错误的bug

</details>


## 许可证

MIT许可证。详情请参阅LICENSE文件。

## Star 经历

[![Star History Chart](https://api.star-history.com/svg?repos=Ikaros-521/AI-Vtuber&type=Date)](https://star-history.com/#Ikaros-521/AI-Vtuber&Date)

## 🤝 贡献

### 🎉 鸣谢

感谢以下开发者对该项目做出的贡献：

<a href="https://github.com/Ikaros-521/AI-Vtuber/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Ikaros-521/AI-Vtuber" />
</a>
<img style="border-radius: 50%; height:66px;" src="https://avatars.githubusercontent.com/u/46062705?v=4" />
