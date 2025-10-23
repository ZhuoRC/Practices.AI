import socket
import threading

# MCP模拟服务器监听设置
HOST = '127.0.0.1'
PORT = 25565

# 当前天气状态
weather_state = 'clear'

def handle_client(conn, addr):
    global weather_state
    print(f"[接入] 来自 {addr} 的连接已建立。")

    with conn:
        while True:
            try:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                print(f"[命令] 收到：{data}")

                if data.startswith("/weather "):
                    cmd = data.split(" ", 1)[1]
                    if cmd in ["clear", "rain", "thunder"]:
                        weather_state = cmd
                        response = f"天气已更改为 {weather_state}。"
                    else:
                        response = f"未知天气命令：{cmd}"
                elif data == "/weather":
                    response = f"当前天气是：{weather_state}"
                elif data == "/quit":
                    response = "断开连接。"
                    conn.sendall(response.encode())
                    break
                else:
                    response = f"未知指令：{data}"

                conn.sendall(response.encode())

            except ConnectionResetError:
                print(f"[断开] {addr} 意外断开。")
                break

    print(f"[结束] 来自 {addr} 的连接关闭。")

def start_server():
    print(f"[启动] MCP Weather Server 启动中，监听 {HOST}:{PORT} ...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
