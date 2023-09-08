@echo off
chcp 65001

pip install -r requirements_bilibili.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements_dy.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements_ks.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements_bilibili.txt -i https://pypi.python.org/simple/
pip install -r requirements_dy.txt -i https://pypi.python.org/simple/
pip install -r requirements_ks.txt -i https://pypi.python.org/simple/

echo 如果都成功了，那没事了，如果有失败的，请手动补装
@REM cmd /k