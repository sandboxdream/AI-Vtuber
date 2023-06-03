## 运行环境
- Python 3.6+

## 安装依赖
在命令行中使用以下命令安装所需库：
```bash
pip install ChatterBot
```
此外，还需要[下载并安装mpv](https://mpv.io/installation/)。在Windows操作系统上，也需要将 `mpv.exe` 添加到环境变量中。对于其他操作系统，请将其路径添加到系统 `PATH` 环境变量中。

如果ChatterBot安装报错，请前往 https://github.com/RaSan147/ChatterBot_update 安装新版本。下载下来输入`python setup.py install`即可

## 如何训练自己的AI？
- 打开`data/db.txt`，写入你想要训练的内容，格式如下
```
问
答
问
答
```
- 将文件重命名为`data/db.txt`
- 在命令行中运行以下命令启动程序：
```bash
python train.py
```
- 训练完的模型名叫`db.sqlite3`，直接双击`main.py`即可使用
- 没有语料？快来加群下载吧！[745682833](https://jq.qq.com/?_wv=1027&k=IO1usMMj)

## 常见问题
1. 提示缺少en-core-web-sm，打开终端输入
```bash
python -m spacy download en_core_web_sm
```
2. 报错：no module named ‘spacy’解决办法
```bash
pip install spacy
```

## 许可证
MIT许可证。详情请参阅LICENSE文件。

## 补充

### ChatterBot
ChatterBot 是一个开源的 Python 聊天机器人框架，使用机器学习算法（尤其是自然语言处理、文本语义分析等）来实现基于规则和语境的自动聊天系统。它可以让开发者通过简单的配置和训练，构建出各种类型的聊天机器人，包括问答机器人、任务型机器人、闲聊机器人等。

ChatterBot 的核心思想是：基于历史对话数据，使用机器学习和自然语言处理技术来分析和预测用户输入，然后生成响应。基于这种方法，聊天机器人的反应会更加智能、灵活、接近人类对话的方式。此外，ChatterBot 支持多种存储方式，如 JSON、SQLAlchemy、MongoDB 等，以及多种接口调用方式，如 RESTful API、WebSocket 等，方便开发者在不同场景中进行集成。

总的来说，ChatterBot 是一个非常强大、灵活、易用的聊天机器人框架，帮助开发者快速搭建出个性化、定制化的聊天机器人，从而提升用户体验和服务质量。