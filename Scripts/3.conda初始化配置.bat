@echo off

rem 获取当前系统用户的用户名
for /f %%i in ('whoami') do set "USERNAME=%%i"

rem 如果无法获取用户名，则默认使用 "Administrator"
if "%USERNAME%"=="" set "USERNAME=Administrator"

rem 设置 Conda 配置文件路径
set "CONDARC_PATH=C:\Users\%USERNAME%\.condarc"

rem 检查配置文件是否已存在
if exist "!CONDARC_PATH!" (
    echo Conda 配置文件已存在，无需初始化。
    exit /b
)

rem 创建 Conda 配置文件
echo 创建 Conda 配置文件...
echo channels: > "!CONDARC_PATH!"
echo   - defaults >> "!CONDARC_PATH!"

rem 初始化 Conda
echo 初始化 Conda...
conda init

echo Conda 配置文件初始化完成。
