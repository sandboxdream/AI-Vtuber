from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer

# 读取语料库文件
with open('data/db.txt', 'r', encoding='utf-8') as f:
    corpus = f.readlines()

# 创建ChatBot实例并训练
my_bot = ChatBot(input('请输入ChatBot名称：'))
trainer = ListTrainer(my_bot)
print('开始训练！')
trainer.train(corpus)
print('训练完毕！')
