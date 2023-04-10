# AI Vtuber

AI Vtuber是一个由ChatterBot驱动的虚拟主播，可以在Bilibili直播中与观众实时互动。它使用自然语言处理和文本转语音技术生成对观众问题的回答。

魔改后的2为VITS版本，可以做复读，也可以沿用原版的ChatterBot进行聊天。

版本3为AI Vtuber Kun的VITS版本。

## 运行环境

### main.py
- Python 3.6+
- Windows操作系统

### main2.py
- Python 3.8+

### main3.py
- Python 3.10+

## main2.py（vits魔改版）

### 安装依赖
在命令行中使用以下命令安装所需库：
```bash
pip install -r requirements2.txt
```
此外，还需要[下载并安装mpv](https://mpv.io/installation/)。在Windows操作系统上，也需要将 `mpv.exe` 添加到环境变量中。对于其他操作系统，请将其路径添加到系统 `PATH` 环境变量中。

如果ChatterBot安装报错，请前往 https://github.com/RaSan147/ChatterBot_update 安装新版本。下载下来输入`python setup.py install`即可

### 前期准备
- live2d模型（可选）  
- 第三方库（装个）：pip install aiohttp langid pypinyin pykakasi pyautogui
- VITS-Fast（合成语音，注意API请求内容，自行适配）

#### live2d模型
伊卡洛斯模型：[https://www.bilibili.com/video/av672172794](https://www.bilibili.com/video/av672172794)

### 使用
修改main2.py的内容，尤其是vits-fast部分的内容，比如`speakers`，配置完毕后运行`python main2.py`即可。


## main.py（原版程序）

### 安装依赖
在命令行中使用以下命令安装所需库：
```bash
pip install -r requirements.txt
```
此外，还需要[下载并安装mpv](https://mpv.io/installation/)。在Windows操作系统上，也需要将 `mpv.exe` 添加到环境变量中。对于其他操作系统，请将其路径添加到系统 `PATH` 环境变量中。

如果ChatterBot安装报错，请前往 https://github.com/RaSan147/ChatterBot_update 安装新版本。下载下来输入`python setup.py install`即可

### 配置
1. 打开 `main.py` 文件并修改 `database_uri` 变量的值以指定用于存储对话历史的SQLite数据库文件的路径。

### 使用
1. 在命令行中运行以下命令启动程序：
```bash
python main.py
```
2. 输入要连接的B站直播间编号。
3. 按下`Enter`键开始监听弹幕流。

当有观众发送弹幕消息时，机器人将自动生成回复并将其转换为语音。声音文件将被保存并立即播放。

### 如何训练自己的AI？
- 打开`db.txt`，写入你想要训练的内容，格式如下
```
问
答
问
答
```
- 将文件重命名为`db.txt`
- 在命令行中运行以下命令启动程序：
```bash
python train.py
```
- 训练完的模型名叫`db.sqlite3`，直接双击`main.py`即可使用
- 没有语料？快来加群下载吧！[745682833](https://jq.qq.com/?_wv=1027&k=IO1usMMj)

### 常见问题
1. 提示缺少en-core-web-sm，打开终端输入
```bash
python -m spacy download en_core_web_sm
```
2. 报错：no module named ‘spacy’解决办法
```bash
pip install spacy
```

### TODO
- [ ] 优化ChatterBot
  - [ ] 重写ChatterBot

### 许可证
MIT许可证。详情请参阅LICENSE文件。

## 扩展

### ChatterBot
ChatterBot 是一个开源的 Python 聊天机器人框架，使用机器学习算法（尤其是自然语言处理、文本语义分析等）来实现基于规则和语境的自动聊天系统。它可以让开发者通过简单的配置和训练，构建出各种类型的聊天机器人，包括问答机器人、任务型机器人、闲聊机器人等。

ChatterBot 的核心思想是：基于历史对话数据，使用机器学习和自然语言处理技术来分析和预测用户输入，然后生成响应。基于这种方法，聊天机器人的反应会更加智能、灵活、接近人类对话的方式。此外，ChatterBot 支持多种存储方式，如 JSON、SQLAlchemy、MongoDB 等，以及多种接口调用方式，如 RESTful API、WebSocket 等，方便开发者在不同场景中进行集成。

总的来说，ChatterBot 是一个非常强大、灵活、易用的聊天机器人框架，帮助开发者快速搭建出个性化、定制化的聊天机器人，从而提升用户体验和服务质量。