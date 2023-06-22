@echo off
chcp 65001
call conda activate ai_vtb
@REM call conda config --add channels https://repo.anaconda.com/pkgs/main
@REM call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
@REM call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
@REM call conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
@REM call conda config --set show_channel_urls yes
@REM call conda install -c https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge openai pygame

echo 激活成功后，在当前窗口内手动运行命令: 2-1.安装依赖.bat
cmd /k