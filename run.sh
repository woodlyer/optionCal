#!/bin/bash

# 自动获取当前脚本所在的目录，即 Flask 应用的根目录
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_FILE="${APP_DIR}/flask_app.log"
PID_FILE="${APP_DIR}/flask_app.pid"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "Flask 应用已经在运行中 (PID: $(cat "$PID_FILE"))."
    else
        echo "正在启动 Flask 应用 (app.py)..."
        cd "${APP_DIR}" || exit 1
        source ./venv/bin/activate
        nohup python3 app.py > "${LOG_FILE}" 2>&1 &
        echo $! > "$PID_FILE"
        echo "应用已启动 (PID: $(cat "$PID_FILE"))."
        echo "日志路径: ${LOG_FILE}"
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        echo "正在停止 Flask 应用 (PID: $PID)..."
        kill "$PID"
        rm "$PID_FILE"
        echo "应用已停止。"
    else
        PID=$(ps aux | grep "python3 app.py" | grep -v grep | awk '{print $2}')
        if [ -n "$PID" ]; then
             echo "未发现 PID 文件，但检测到进程 $PID，正在强制停止..."
             kill "$PID"
             echo "已停止。"
        else
             echo "未发现正在运行的应用。"
        fi
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "状态: 正在运行 (PID: $(cat "$PID_FILE"))"
    else
        echo "状态: 未运行"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
