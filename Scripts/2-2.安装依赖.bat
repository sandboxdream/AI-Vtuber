@echo off
chcp 65001

Miniconda3\python.exe -m pip install -r requirements_bilibili.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Miniconda3\python.exe -m pip install -r requirements_dy.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Miniconda3\python.exe -m pip install -r requirements_ks.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
Miniconda3\python.exe -m pip install -r requirements_bilibili.txt -i https://pypi.python.org/simple/
Miniconda3\python.exe -m pip install -r requirements_dy.txt -i https://pypi.python.org/simple/
Miniconda3\python.exe -m pip install -r requirements_ks.txt -i https://pypi.python.org/simple/

echo 如果都成功了，那没事了，如果有失败的，请手动补装
cmd /k