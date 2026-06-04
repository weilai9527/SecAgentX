@echo off
chcp 65001 >nul
echo ==========================================
echo SecAgentX 启动脚本
echo ==========================================
echo.

set BACKEND_DIR=%~dp0backend
set FRONTEND_DIR=%~dp0frontend

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请安装 Python 3.10+
    pause
    exit /b 1
)

:: Install backend dependencies
echo [1/4] 安装后端依赖...
cd /d "%BACKEND_DIR%"
python -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [警告] 依赖安装可能存在问题，继续尝试启动...
)

:: Start backend
echo [2/4] 启动后端服务 (http://127.0.0.1:8000)...
start "SecAgentX Backend" cmd /k "cd /d %BACKEND_DIR% && python run.py"

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未检测到 Node.js，跳过前端启动。请手动安装 Node.js 后运行 npm run dev
    pause
    exit /b 0
)

:: Install frontend dependencies
echo [3/4] 安装前端依赖...
cd /d "%FRONTEND_DIR%"
call npm install

:: Start frontend
echo [4/4] 启动前端服务 (http://127.0.0.1:5173)...
start "SecAgentX Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm run dev"

echo.
echo ==========================================
echo SecAgentX 已启动！
echo 后端: http://127.0.0.1:8000
echo 前端: http://127.0.0.1:5173
echo ==========================================
pause
