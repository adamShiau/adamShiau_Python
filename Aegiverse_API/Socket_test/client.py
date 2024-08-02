import socket

# 創建 socket 對象
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 連接伺服器
client_socket.connect(('localhost', 12345))

# 發送數據
client_socket.sendall(b"Hello, Server")

# 接收數據
data = client_socket.recv(1024)
print(f"Client Received: {data.decode()}")

# 關閉連接
client_socket.close()
