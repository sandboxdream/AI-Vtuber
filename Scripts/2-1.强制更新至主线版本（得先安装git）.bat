@echo off
chcp 65001
where git > nul 2>&1
if %errorlevel% neq 0 (
    echo Git 命令没找到，请先安装git客户端.
    pause
    exit /b
)

git fetch --all
git reset --hard origin/main
echo 拉取完毕（如果没报错的话）.
pause