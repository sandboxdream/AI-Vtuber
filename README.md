# AI Vtuber

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

AI Vtuber是一个由`ChatterBot/GPT/Claude/langchain_pdf+gpt`驱动的虚拟主播，可以在`Bilibili/抖音`直播中与观众实时互动。它使用自然语言处理和文本转语音技术(`Edge-TTS/VITS-Fast/elevenlabs`)生成对观众问题的回答。

`bilibili`文件夹，哔哩哔哩版本，含原始项目版本，vits改版，大融合版本。  

`douyin`文件夹，抖音版的大融合功能。  

2个平台的使用说明在各自文件夹内的README.md中有写。  

## 运行环境
python：3.10  
依赖的库在 requirements.txt 中，请自行安装。  

## 许可证
MIT许可证。详情请参阅LICENSE文件。

## 补充

### langchain_pdf
参考：[LangChainSummarize](https://github.com/Ikaros-521/LangChainSummarize)  

### elevenlabs
[elevenlabs官网](https://beta.elevenlabs.io/)  
[官方文档](https://docs.elevenlabs.io/api-reference/quick-start/introduction)  
不注册账号也可以使用，不过应该是有限制的（具体多少未知）。免费账号拥有每月1万字的额度。  

### ChatterBot
ChatterBot 是一个开源的 Python 聊天机器人框架，使用机器学习算法（尤其是自然语言处理、文本语义分析等）来实现基于规则和语境的自动聊天系统。它可以让开发者通过简单的配置和训练，构建出各种类型的聊天机器人，包括问答机器人、任务型机器人、闲聊机器人等。

ChatterBot 的核心思想是：基于历史对话数据，使用机器学习和自然语言处理技术来分析和预测用户输入，然后生成响应。基于这种方法，聊天机器人的反应会更加智能、灵活、接近人类对话的方式。此外，ChatterBot 支持多种存储方式，如 JSON、SQLAlchemy、MongoDB 等，以及多种接口调用方式，如 RESTful API、WebSocket 等，方便开发者在不同场景中进行集成。

总的来说，ChatterBot 是一个非常强大、灵活、易用的聊天机器人框架，帮助开发者快速搭建出个性化、定制化的聊天机器人，从而提升用户体验和服务质量。