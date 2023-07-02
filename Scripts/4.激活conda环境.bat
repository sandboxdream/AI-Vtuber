@echo off
chcp 65001
color 0a
set CONDA=%~dp0\Miniconda3\condabin\conda.bat
call %CONDA% config --add channels conda-forge
call %CONDA% config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
call %CONDA% config --set show_channel_urls yes 
cls
call %CONDA% info
cmd "/K" %~dp0\Miniconda3\Scripts\activate.bat %~dp0\Miniconda3
