#!/bin/bash
set -e

echo "=========================================="
echo "SecAgentX 启动脚本"
echo "=========================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Backend
echo "[1/3] 安装后端依赖..."
cd "$BACKEND_DIR"
python3 -m pip install -r requirements.txt -q

echo "[2/3] 启动后端服务 (http://127.0.0.1:8000)..."
osascript -e 'tell app "Terminal" to do script "cd '"$BACKEND_DIR"'; python3 run.py"' 2>/dev/null || \
    (python3 run.py &)

# Frontend
echo "[3/3] 启动前端服务 (http://127.0.0.1:5173)..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    npm install
fi
osascript -e 'tell app "Terminal" to do script "cd '"$FRONTEND_DIR"'; npm run dev"' 2>/dev/null || \
    (npm run dev &)

echo ""
echo "=========================================="
echo "SecAgentX 已启动！"
echo "后端: http://127.0.0.1:8000"
echo "前端: http://127.0.0.1:5173"
echo "=========================================="
