@echo off
chcp 65001 > nul 2>&1

REM 设置文件列表，可以包含多个文件路径和文件夹路径，每个路径用空格分隔
set "file_list="
set "file_list=%file_list% data\copywriting\test.txt data\copywriting\测试文案.txt data\copywriting\测试文案2.txt data\copywriting\测试文案3.txt data\copywriting\达达利亚.txt data\copywriting\吐槽.txt data\copywriting\伊卡日语介绍.txt"
set "file_list=%file_list% data\copywriting2\test.txt data\copywriting2\test2.txt data\copywriting2\测试文案.txt"
set "file_list=%file_list% data\伊卡洛斯百度百科.pdf"
set "file_list=%file_list% log\*.txt log\*.log"
set "file_list=%file_list% out\*.wav out\*.mp3"
set "file_list=%file_list% out\copywriting\test.wav out\copywriting\测试文案.mp3 out\copywriting\测试文案.wav out\copywriting\测试文案2.wav out\copywriting\测试文案3.wav out\copywriting\达达利亚.wav out\copywriting\吐槽.wav out\copywriting\伊卡日语介绍.wav"
set "file_list=%file_list% out\copywriting2\test.wav out\copywriting2\test2.wav"
set "file_list=%file_list% out\本地问答音频\关键词1.wav out\本地问答音频\关键词2.wav"
set "file_list=%file_list% out\song\把回忆拼好给你.mp3"
set "folder_list=预留变量"

REM 循环遍历文件列表并删除文件
for %%F in (%file_list%) do (
    if exist "%%F" (
        del /f /q "%%F"
        echo 删除文件 '%%F' 成功。
    ) else (
        echo 文件 '%%F' 不存在，无需删除。
    )
)

REM 循环遍历文件夹列表并删除文件夹
for %%D in (%folder_list%) do (
    if exist "%%D" (
        rd /s /q "%%D"
        echo 删除文件夹 '%%D' 成功。
    ) else (
        echo 文件夹 '%%D' 不存在，无需删除。
    )
)

REM 这里是脚本的其他部分，不会因为文件或文件夹不存在而受影响，可以继续运行。
pause
